
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
    prompt = TEACHER_PROMPT.format(topic=state['topic'], grade_level=state['grade_level'])
    messages = [SystemMessage(content=prompt)] + state['messages']
    response = llm.invoke(messages)
    return {"messages": [response], "current_action": "EXPLAINING", "next_dest": "END"}

def problem_node(state: AgentState):
    prompt = PROBLEM_GENERATOR_PROMPT.format(
        topic=state['topic'],
        concept=state['topic'], 
        grade_level=state['grade_level']
    )
    # We ignore history for problem generation usually, or keep it short
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"messages": [response], "current_action": "PROBLEM_GIVEN", "last_problem": response.content, "next_dest": "END"}

def verifier_node(state: AgentState):
    last_answer = state['messages'][-1].content
    prompt = VERIFIER_PROMPT.format(
        last_problem=state.get('last_problem', 'Unknown'),
        last_answer=last_answer
    )
    response = llm.invoke([SystemMessage(content=prompt)])
    return {"messages": [response], "current_action": "IDLE", "next_dest": "END"}

def chat_node(state: AgentState):
    response = llm.invoke(state['messages'])
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

