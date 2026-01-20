
import operator
from typing import TypedDict, List, Annotated, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from .prompts import TEACHER_PROMPT, PROBLEM_GENERATOR_PROMPT, VERIFIER_PROMPT, SUPERVISOR_PROMPT

# State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    topic: str
    grade_level: str
    location: str # New field
    learning_style: str # New field
    current_action: str # "IDLE", "PROBLEM_GIVEN", "EXPLAINING"
    last_problem: str
    next_dest: str # Used for routing

# LLM
llm = ChatOpenAI(model="gpt-4o")

# Nodes
def supervisor_node(state: AgentState):
    messages = state['messages']
    last_user_msg = messages[-1].content
    
    # Simple logic mapping for robust routing (LLM can be flaky with formatting)
    prompt = SUPERVISOR_PROMPT.format(
        last_message=last_user_msg,
        last_action=state.get('current_action', 'IDLE')
    )
    
    # We use a smaller model or force json for supervisor mostly, 
    # but here just text classification
    decision_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    response = decision_llm.invoke(prompt)
    decision = response.content.strip().upper()
    
    # Fallback
    valid_dests = ["VERIFIER", "TEACHER", "PROBLEM_GENERATOR", "GENERAL_CHAT"]
    found = False
    for v in valid_dests:
        if v in decision:
            decision = v
            found = True
            break
    if not found:
        decision = "GENERAL_CHAT"
        
    return {"next_dest": decision}

def teacher_node(state: AgentState):
    loc = state.get("location", "New Hampshire")
    style = state.get("learning_style", "Universal")
    
    # Append style instruction
    style_instruction = f"\nStudent Learning Style: {style}. Adapt your explanation accordingly."
    
    prompt = TEACHER_PROMPT.format(
        topic=state['topic'], 
        grade_level=state['grade_level'],
        location=loc
    ) + style_instruction
    
    print(f"\n[AGENTS] TEACHER NODE\nPROMPT:\n{prompt}\n")
    messages = [SystemMessage(content=prompt)] + state['messages']
    response = llm.invoke(messages)
    print(f"RESPONSE:\n{response.content}\n")
    return {"messages": [response], "current_action": "EXPLAINING", "next_dest": "END"}

def problem_node(state: AgentState):
    prompt = PROBLEM_GENERATOR_PROMPT.format(
        topic=state['topic'],
        concept=state['topic'], 
        grade_level=state['grade_level']
    )
    print(f"\n[AGENTS] PROBLEM NODE\nPROMPT:\n{prompt}\n")
    # We ignore history for problem generation usually, or keep it short
    response = llm.invoke([SystemMessage(content=prompt)])
    print(f"RESPONSE:\n{response.content}\n")
    return {"messages": [response], "current_action": "PROBLEM_GIVEN", "last_problem": response.content, "next_dest": "END"}

def verifier_node(state: AgentState):
    messages = state['messages']
    last_answer = messages[-1].content
    
    # Try to get problem from state, fallback to last AI message
    problem_context = state.get('last_problem')
    if not problem_context or problem_context == "Unknown":
        # Find last AI message (skip the last human message)
        if len(messages) >= 2 and isinstance(messages[-2], BaseMessage): # basic check
             problem_context = messages[-2].content
        else:
             problem_context = "Unknown context. Please ask the student to restate the problem."

    prompt = VERIFIER_PROMPT.format(
        last_problem=problem_context,
        last_answer=last_answer
    )
    print(f"\n[AGENTS] VERIFIER NODE\nPROMPT:\n{prompt}\n")
    response = llm.invoke([SystemMessage(content=prompt)])
    print(f"RESPONSE:\n{response.content}\n")
    return {"messages": [response], "current_action": "IDLE", "next_dest": "END"}

def chat_node(state: AgentState):
    print(f"\n[AGENTS] GENERAL CHAT NODE\nMessages: {state['messages']}\n")
    response = llm.invoke(state['messages'])
    print(f"RESPONSE:\n{response.content}\n")
    return {"messages": [response], "next_dest": "END"}

# Initializer Node (optional, can just init state)

# Routing function
def route_step(state: AgentState):
    dest = state.get("next_dest", "GENERAL_CHAT")
    if dest == "VERIFIER":
        return "verifier"
    elif dest == "TEACHER":
        return "teacher"
    elif dest == "PROBLEM_GENERATOR":
        return "problem_generator"
    elif dest == "GENERAL_CHAT":
        return "general_chat"
    return "general_chat"

# Graph Construction
def create_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("teacher", teacher_node)
    builder.add_node("problem_generator", problem_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("general_chat", chat_node)
    
    builder.set_entry_point("supervisor")
    
    builder.add_conditional_edges(
        "supervisor",
        route_step,
        {
            "verifier": "verifier",
            "teacher": "teacher",
            "problem_generator": "problem_generator",
            "general_chat": "general_chat"
        }
    )
    
    builder.add_edge("teacher", END)
    builder.add_edge("problem_generator", END)
    builder.add_edge("verifier", END)
    builder.add_edge("general_chat", END)
    
    return builder

# graph = create_graph() # moved to main

