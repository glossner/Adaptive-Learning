
import operator
from typing import TypedDict, List, Annotated, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END
from .prompts import TEACHER_PROMPT, PROBLEM_GENERATOR_PROMPT, VERIFIER_PROMPT, SUPERVISOR_PROMPT, ADAPTER_PROMPT
from .database import log_interaction, get_db, Player, TopicProgress, SessionLocal
from .knowledge_graph import get_graph, get_all_subjects_stats
import json 

# State Definition
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    topic: str
    grade_level: str
    location: str
    learning_style: str
    username: str
    mastery: int
    current_action: str
    last_problem: str
    next_dest: str

# LLM
llm = ChatOpenAI(model="gpt-4o")

# Nodes
def supervisor_node(state: AgentState):
    messages = state['messages']
    last_user_msg = messages[-1].content
    
    # Simple logic mapping for robust routing
    prompt = SUPERVISOR_PROMPT.format(
        last_message=last_user_msg,
        last_action=state.get('current_action', 'IDLE')
    )
    
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
    
    style_instruction = f"\nStudent Learning Style: {style}. Adapt your explanation accordingly."
    
    kg = get_graph(state['topic'])
    current_node = None
    
    db = SessionLocal()
    try:
        player = db.query(Player).filter(Player.username == state["username"]).first()
        if player:
            prog = db.query(TopicProgress).filter(
                TopicProgress.player_id == player.id, 
                TopicProgress.topic_name == state['topic']
            ).first()
            if prog:
                if prog.current_node:
                    n = kg.get_node(prog.current_node)
                    if n: current_node = n
                
                if not current_node:
                    completed = prog.completed_nodes or []
                    candidates = kg.get_next_learnable_nodes(completed)
                    if candidates:
                        current_node = candidates[0]
                        prog.current_node = current_node.id
                        db.commit()
                        print(f"[KG] Teaching Next Node: {current_node.label}")
                    else:
                        print("[KG] No more nodes or all complete!")
    finally:
        db.close()
    
    topic_label = state['topic']
    if current_node:
        topic_label = f"{state['topic']}: {current_node.label} ({current_node.description})"
        
    prompt = TEACHER_PROMPT.format(
        topic=topic_label, 
        grade_level=state['grade_level'],
        location=loc,
        mastery=state.get('mastery', 0)
    ) + style_instruction
    
    print(f"\n[AGENTS] TEACHER NODE\nPROMPT:\n{prompt}\n")
    messages = [SystemMessage(content=prompt)] + state['messages']
    response = llm.invoke(messages)
    print(f"RESPONSE:\n{response.content}\n")
    
    log_interaction(
        username=state.get("username", "Unknown"),
        subject=state.get("topic", "General"),
        user_query=state['messages'][-1].content if state['messages'] else "",
        agent_response=response.content,
        source_node="teacher"
    )
    
    done_unit, total_unit = 0, 0
    done_subj, total_subj = 0, 0
    done_grade, total_grade = 0, 0
    subtree_root = None
    
    if player and db:
         try:
             prog = db.query(TopicProgress).filter(
                 TopicProgress.player_id == player.id, 
                 TopicProgress.topic_name == state['topic']
             ).first()
             
             print(f"[TEACHER DEBUG] Topic: {state['topic']}, Player: {player.username}")
             if prog and prog.completed_nodes:
                 # Determine Scope: Use the first part of the current node or last completed node
                 # Node ID format: "Arithmetic->Number_Sense->..."
                 # We want "Arithmetic" as the scope.
                 reference_node = None
                 if current_node:
                     reference_node = current_node.id
                 elif prog.completed_nodes:
                     reference_node = prog.completed_nodes[-1]
                     
                 # Unit Mastery (Scope to immediate parent for granular feedback)
                 # e.g. "Arithmetic->Number_Sense->Comparisons->Equality" -> Scope: "Arithmetic->Number_Sense->Comparisons"
                 subtree_root = None
                 if reference_node and "->" in reference_node:
                     parts = reference_node.split("->")
                     if len(parts) > 1:
                         # Use parent path
                         subtree_root = "->".join(parts[:-1])
                     else:
                         subtree_root = parts[0]
                         
                     print(f"[TEACHER DEBUG] Scoping Mastery to Subtree: {subtree_root}")
                 
                 # Unit Mastery
                 done_unit, total_unit = kg.get_completion_stats(prog.completed_nodes, subtree_root)
                 print(f"[TEACHER DEBUG] Unit Stats ({subtree_root or 'ALL'}): Done={done_unit}, Total={total_unit}")
                 
                 # Subject Mastery (Math)
                 done_subj, total_subj = kg.get_completion_stats(prog.completed_nodes)
                 print(f"[TEACHER DEBUG] Subject Stats: Done={done_subj}, Total={total_subj}")
                 
             # Grade Mastery (All Subjects) - Heavy, but robust
             done_grade, total_grade = get_all_subjects_stats(player.id, db)
             print(f"[TEACHER DEBUG] Grade Stats: Done={done_grade}, Total={total_grade}")
                 
         except Exception as e:
             print(f"[TEACHER DEBUG] Error calculating mastery: {e}")
             pass
             
    mastery_data = {
        "unit": 0.0,
        "subject": 0.0,
        "grade": 0.0
    }
    
    if total_unit > 0: mastery_data["unit"] = round((done_unit / total_unit) * 100, 1)
    if total_subj > 0: mastery_data["subject"] = round((done_subj / total_subj) * 100, 1)
    if total_grade > 0: mastery_data["grade"] = round((done_grade / total_grade) * 100, 1)
    
    print(f"[TEACHER DEBUG] Final Mastery Data: {mastery_data}")
    
    return {"messages": [response], "current_action": "EXPLAINING", "next_dest": "END", "mastery": mastery_data}

def problem_node(state: AgentState):
    from .database import get_mistakes
    mistakes = get_mistakes(state.get("username"), state.get("topic"))
    
    reinforcement_instruction = ""
    if mistakes:
        recent_mistakes = list(set(mistakes[-3:]))
        reinforcement_instruction = f"\n\n**Reinforcement**: The student previously struggled with: {recent_mistakes}. Create a problem that specifically targets these weaknesses to reinforce understanding."

    topic_broad = state['topic']
    
    prompt = PROBLEM_GENERATOR_PROMPT.format(
        topic=topic_broad,
        grade_level=state['grade_level']
    ) + reinforcement_instruction
    
    print(f"\n[AGENTS] PROBLEM NODE\nPROMPT:\n{prompt}\n")
    
    context_messages = state['messages'][-5:] 
    full_input = [SystemMessage(content=prompt)] + context_messages
    
    response = llm.invoke(full_input)
    print(f"RESPONSE:\n{response.content}\n")
    
    log_interaction(
        username=state.get("username", "Unknown"),
        subject=topic_broad,
        user_query="[System Triggered Problem Generation]",
        agent_response=response.content,
        source_node="problem_generator"
    )
    
    return {"messages": [response], "current_action": "PROBLEM_GIVEN", "last_problem": response.content, "next_dest": "END"}

def verifier_node(state: AgentState):
    messages = state['messages']
    last_answer = messages[-1].content
    problem_context = state.get('last_problem', 'Unknown')
    
    if not problem_context or problem_context == "Unknown":
        if len(messages) >= 2 and isinstance(messages[-2], BaseMessage):
             problem_context = messages[-2].content
        else:
             problem_context = "Unknown context. Please ask the student to restate the problem."

    prompt = VERIFIER_PROMPT.format(last_problem=problem_context, last_answer=last_answer)
    print(f"\n[AGENTS] VERIFIER NODE\nPROMPT:\n{prompt}\n")
    
    response = llm.invoke([SystemMessage(content=prompt)])
    content = response.content
    print(f"RESPONSE:\n{content}\n")
    
    log_interaction(state.get("username"), state.get("topic"), last_answer, content, "verifier")
    
    # Pass to Adapter
    return {"messages": [response], "next_dest": "ADAPTER"}

def adapter_node(state: AgentState):
    """
    Decides on Mastery vs Remediation based on history.
    """
    topic = state.get("topic", "General")
    messages = state['messages']
    
    # Extract recent interaction history (last 10 messages) for context
    history_str = ""
    for m in messages[-10:]:
        role = "Student: " if isinstance(m, HumanMessage) else "Agent: "
        history_str += f"{role}{m.content}\n"
        
    prompt = ADAPTER_PROMPT.format(topic=topic, history=history_str)
    
    print(f"\n[AGENTS] ADAPTER NODE\nPROMPT:\n{prompt}\n")
    
    # Force JSON output
    adapter_llm = ChatOpenAI(model="gpt-4o", model_kwargs={"response_format": {"type": "json_object"}})
    response = adapter_llm.invoke([SystemMessage(content=prompt)])
    content = response.content
    print(f"RESPONSE:\n{content}\n")
    
    decision_data = {}
    try:
        decision_data = json.loads(content)
    except:
        print("Adapter JSON Parse Error")
        decision_data = {"decision": "CONTINUE_PRACTICE"}
        
    decision = decision_data.get("decision", "CONTINUE_PRACTICE")
    remediation_topic = decision_data.get("remediation_topic")
    
    # DB Logic
    user = state.get("username", "Player1")
    new_mastery = -1
    
    if decision == "MASTERED":
        # Mark Complete in DB
        kg = get_graph(topic)
        completed = []
        db = SessionLocal()
        try:
             player = db.query(Player).filter(Player.username == user).first()
             if player:
                prog = db.query(TopicProgress).filter(
                    TopicProgress.player_id == player.id, 
                    TopicProgress.topic_name == topic
                ).first()
                if prog and prog.current_node:
                    completed = list(prog.completed_nodes) if prog.completed_nodes else []
                    if prog.current_node not in completed:
                        completed.append(prog.current_node)
                        prog.completed_nodes = completed
                        prog.current_node = None
                        db.commit()
                        print(f"[KG] Node Mastered by Adapter!")
                        
                    # Calculate Multi-Level Mastery
                    subtree_root = None
                    if completed and "->" in completed[-1]:
                         parts = completed[-1].split("->")
                         if len(parts) > 1:
                             subtree_root = "->".join(parts[:-1])
                         else:
                             subtree_root = parts[0]
                         
                    done_unit, total_unit = kg.get_completion_stats(completed, subtree_root)
                    done_subj, total_subj = kg.get_completion_stats(completed)
                    
                    if total_subj > 0:
                        prog.mastery_score = int((done_subj / total_subj) * 100) # Persist Subject Mastery
                        db.commit()
                        
                    done_grade, total_grade = get_all_subjects_stats(player.id, db)
                    
        finally:
            db.close()
            
        mastery_data = {
            "unit": 0.0, "subject": 0.0, "grade": 0.0
        }
        if total_unit > 0: mastery_data["unit"] = round((done_unit / total_unit) * 100, 1)
        if total_subj > 0: mastery_data["subject"] = round((done_subj / total_subj) * 100, 1)
        if total_grade > 0: mastery_data["grade"] = round((done_grade / total_grade) * 100, 1)
            
        # Auto-Advance Logic
        candidates = kg.get_next_learnable_nodes(completed)
        
        if len(candidates) == 1:
             # Auto-advance
             next_label = candidates[0].label
             msg = AIMessage(content=f"Excellent work! You've mastered {topic}. Auto-advancing to: {next_label}...")
             return {"messages": [msg], "current_action": "EXPLAINING", "next_dest": "TEACHER", "mastery": new_mastery}
        elif len(candidates) > 1:
             # Choice needed
             options_str = ", ".join([c.label for c in candidates[:3]])
             msg = AIMessage(content=f"Excellent! {topic} mastered. Next options: {options_str}. What would you like to learn?")
             return {"messages": [msg], "current_action": "IDLE", "next_dest": "END", "mastery": new_mastery}

        # Finished
        msg = AIMessage(content=f"Excellent work! You've mastered {topic}. Let's move on!")
        return {"messages": [msg], "current_action": "IDLE", "next_dest": "END", "mastery": new_mastery}

    elif decision == "REMEDIATE" and remediation_topic:
        # Find Prereq
        kg = get_graph(topic)
        db = SessionLocal()
        target_remediation = None
        try:
            player = db.query(Player).filter(Player.username == user).first()
            prog = db.query(TopicProgress).filter(TopicProgress.player_id == player.id, TopicProgress.topic_name == topic).first()
            if prog and prog.current_node:
                current_node_id = prog.current_node
                prereqs = kg.get_prerequisites(current_node_id)
                if prereqs:
                    target_remediation = prereqs[0] # Pick first one
        finally:
            db.close()
            
        if target_remediation:
             msg = AIMessage(content=f"It seems we should review a prerequisite: {target_remediation}. Let's switch focus.")
             return {"messages": [msg], "current_action": "IDLE", "next_dest": "TEACHER"} 
        
    # Default: Continue
    return {"messages": [], "next_dest": "PROBLEM_GENERATOR"}

def chat_node(state: AgentState):
    print(f"\n[AGENTS] GENERAL CHAT NODE\nMessages: {state['messages']}\n")
    response = llm.invoke(state['messages'])
    print(f"RESPONSE:\n{response.content}\n")
    
    log_interaction(
        username=state.get("username", "Unknown"),
        subject="General",
        user_query=state['messages'][-1].content if state['messages'] else "",
        agent_response=response.content,
        source_node="general_chat"
    )
    
    return {"messages": [response], "next_dest": "END"}

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
    elif dest == "ADAPTER":
        return "adapter"
    elif dest == "END":
        return "end"
    return "general_chat"

# Graph Construction
def create_graph():
    builder = StateGraph(AgentState)
    
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("teacher", teacher_node)
    builder.add_node("problem_generator", problem_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("adapter", adapter_node)
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
    
    builder.add_edge("verifier", "adapter")
    
    builder.add_conditional_edges(
        "adapter", 
        route_step,
        {
            "teacher": "teacher",
            "problem_generator": "problem_generator",
            "general_chat": "general_chat",
            "end": END
        }
    )
    
    builder.add_edge("teacher", END)
    builder.add_edge("problem_generator", END)
    builder.add_edge("general_chat", END)
    
    return builder
