from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .models import InitRequest, ChatRequest, ChatResponse, BookSelectRequest, BookSelectResponse, InitSessionRequest, InitSessionResponse, ResumeShelfRequest, ResumeShelfResponse, PlayerStatsRequest, GraphDataRequest, GraphDataResponse, GraphNode, SetCurrentNodeRequest
from .graph import create_graph
from .database import init_db, get_db, Player, TopicProgress
import uuid
import json

# Global graph instance
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    init_db()
    checkpointer = MemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=checkpointer)
    print("Graph compiled with MemorySaver.")
    yield
    print("Shutting down.")

app = FastAPI(lifespan=lifespan)

@app.get("/get_users", response_model=List[str])
async def get_users_list(db: Session = Depends(get_db)):
    from .database import get_all_users
    return get_all_users()

@app.post("/get_player_stats")
async def get_player_stats(request: PlayerStatsRequest, db: Session = Depends(get_db)):
    # Calculate stats for all subjects for the Library UI
    from .knowledge_graph import get_graph, get_all_subjects_stats
    
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        return {"stats": {}}
        
    stats = {}
    subjects = ["math", "science", "history", "english"]
    
    for subj in subjects:
        # DB Topic Name (Capitalized)
        db_topic = subj.capitalize()
        if subj == "english": db_topic = "English"
        
        # Get Progress
        prog = db.query(TopicProgress).filter(
            TopicProgress.player_id == player.id,
            TopicProgress.topic_name == db_topic
        ).first()
        
        # Get KG
        kg = get_graph(subj)
        
        done, total = 0, 0
        if prog and prog.completed_nodes:
            done, total = kg.get_completion_stats(prog.completed_nodes)
            
        percent = 0.0
        if total > 0:
            percent = round((done / total) * 100, 1)
            
        stats[subj] = percent
        
    # Calculate Overall Grade Completion
    done_grade, total_grade = get_all_subjects_stats(player.id, db)
    grade_percent = 0.0
    if total_grade > 0:
        grade_percent = round((done_grade / total_grade) * 100, 1)
        
    stats["grade_completion"] = grade_percent
    stats["current_grade_level"] = player.grade_level
        
    return {"stats": stats}

@app.post("/select_book", response_model=BookSelectResponse)
async def select_book(request: BookSelectRequest, db: Session = Depends(get_db)):
    # 1. Get or Create Player
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        # Defaults: Grade 10, New Hampshire
        player = Player(username=request.username, location="New Hampshire", grade_level=10)
        db.add(player)
        db.commit()
        db.refresh(player)
    
    # 2. Get or Create Topic Progress
    progress = db.query(TopicProgress).filter(
        TopicProgress.player_id == player.id,
        TopicProgress.topic_name == request.topic
    ).first()
    
    resume_summary = None
    adaptive_suggestion = ""
    
    # CRITICAL: Use Session Grade if provided (Transient Session Support)
    current_grade_level = player.grade_level
    if request.session_grade_level is not None:
        current_grade_level = request.session_grade_level

    # 3. Adaptive Logic: Check Grade Level
    # Extract number from topic string (e.g. "History 1" -> 1)
    import re
    topic_grade_match = re.search(r'\d+', request.topic)
    if topic_grade_match:
        topic_grade = int(topic_grade_match.group())
        
        # Determine gap
        grade_diff = current_grade_level - topic_grade
        
        # 1. Manual Mode: Always accept.
        if request.manual_mode:
            adaptive_suggestion = ""
            
        # 2. Lower Grade (Review Mode)
        elif grade_diff > 0:
            adaptive_suggestion = f"\n\n[System]: Review Mode initialized. You are Grade {current_grade_level}, reviewing Grade {topic_grade} material."
            
        # 4. Higher Grade (Challenge?)
        elif grade_diff < -2:
             adaptive_suggestion = f"\n\n[System]: Challenge Mode. You are Grade {current_grade_level} attempting Grade {topic_grade}. Good luck!"
             
    # CRITICAL: Logic update to accept string from UI
    effective_grade = f"Grade {current_grade_level}"
    if topic_grade_match:
         if request.manual_mode or (current_grade_level != topic_grade):
             effective_grade = f"Grade {topic_grade_match.group()}"

    if not progress:
        progress = TopicProgress(player_id=player.id, topic_name=request.topic)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    else:
        resume_summary = f"Continuing {request.topic}. Mastery: {progress.mastery_score}%"

    full_summary = (resume_summary or f"Starting {request.topic}.") + adaptive_suggestion

    # 4. Initialize Graph Session
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    initial_state = {
        "topic": request.topic,
        "grade_level": effective_grade, 
        "location": player.location,
        "learning_style": player.learning_style,
        "username": player.username,
        "mastery": progress.mastery_score,
        "messages": [], 
        "current_action": "IDLE",
        "last_problem": "",
        "next_dest": "GENERAL_CHAT"
    }
    
    # In a real heavy app, we'd load 'last_state_snapshot' from DB into graph
    # But for now we just spin up a session.
    await graph.aupdate_state(config, initial_state)
    
    # [NEW] Inject Navigation Context for Initial Load
    state_snapshot = {"current_action": "IDLE", "mastery": progress.mastery_score}
    try:
        from .knowledge_graph import get_graph
        kg_subj = get_graph(request.topic)
        
        # Current
        if progress.current_node:
            n = kg_subj.get_node(progress.current_node)
            if n: state_snapshot["current_node_label"] = n.label
            
        # Previous
        if progress.completed_nodes:
             prev_id = progress.completed_nodes[-1]
             prev_n = kg_subj.get_node(prev_id)
             if prev_n: state_snapshot["prev_node_label"] = prev_n.label
             
        # Next (Suggestion)
        completed_list = list(progress.completed_nodes) if progress.completed_nodes else []
        temp_completed = list(completed_list)
        if progress.current_node and progress.current_node not in temp_completed:
            temp_completed.append(progress.current_node)
        
        nav_options = navigator.get_next_options(temp_completed, player.grade_level)
        if nav_options:
            next_path = nav_options[0]
            if "->" in next_path:
                state_snapshot["next_node_label"] = next_path.split("->")[-1]
            else:
                state_snapshot["next_node_label"] = next_path
                
    except Exception as e:
        print(f"Error injecting nav context in select_book: {e}")
    
    return BookSelectResponse(
        session_id=session_id,
        status=progress.status,
        xp=player.xp,
        level=player.level,
        mastery=progress.mastery_score,
        history_summary=full_summary,
        state_snapshot=state_snapshot
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    config = {"configurable": {"thread_id": request.session_id}}
    
    current_state = await graph.aget_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    inputs = {"messages": [HumanMessage(content=request.message)]}
    print(f"\n[API] /chat Request: {request.message}")
    result = await graph.ainvoke(inputs, config)
    
    messages = result.get("messages", [])
    last_msg = messages[-1].content if messages else ""
    current_action = result.get("current_action", "IDLE")

    print(f"[API] /chat Response: {last_msg}\n")
    
    # Extract mastery if updated
    mastery_update = result.get("mastery")
    
    snapshot = {"current_action": current_action}
    if mastery_update is not None:
        snapshot["mastery"] = mastery_update
    
    # [NEW] Inject Navigation Context (Current/Prev/Next)
    # This adds slight overhead but is required for UI
    try:
        player = db.query(Player).filter(Player.username == current_state.values.get("username")).first()
        topic_name = current_state.values.get("topic")
        if player and topic_name:
            prog = db.query(TopicProgress).filter(TopicProgress.player_id == player.id, TopicProgress.topic_name == topic_name).first()
            if prog:
                # Current
                if prog.current_node:
                    kg_subj = get_graph(topic_name)
                    n = kg_subj.get_node(prog.current_node)
                    if n: snapshot["current_node_label"] = n.label
                
                # Previous (Last master topic)
                if prog.completed_nodes:
                     prev_id = prog.completed_nodes[-1]
                     kg_subj = get_graph(topic_name)
                     prev_n = kg_subj.get_node(prev_id)
                     if prev_n: snapshot["prev_node_label"] = prev_n.label
                     
                # Next (Suggestion)
                completed_list = list(prog.completed_nodes) if prog.completed_nodes else []
                # Use current node as marking "active", so next is usually AFTER current completes.
                # But UI asks for "Next Topic" which implies "What is coming up?".
                # If we are working on Current, Next is the one after Current.
                # Temporarily add current to completed to see what comes next?
                temp_completed = list(completed_list)
                if prog.current_node and prog.current_node not in temp_completed:
                    temp_completed.append(prog.current_node)
                
                nav_options = navigator.get_next_options(temp_completed, player.grade_level)
                if nav_options:
                    # Parse label from ID? ID is Path. Label is last part usually?
                    # Or get node.
                    # navigator return paths.
                    next_path = nav_options[0]
                    # Format: ...->Label
                    if "->" in next_path:
                        snapshot["next_node_label"] = next_path.split("->")[-1]
                    else:
                        snapshot["next_node_label"] = next_path
                        
    except Exception as e:
        print(f"Error injecting nav context: {e}")

    return ChatResponse(
        response=str(last_msg),
        state_snapshot=snapshot
    )

# Initialize GraphNavigator
from .graph_logic import GraphNavigator
navigator = GraphNavigator()

@app.post("/update_progress")
async def update_progress(username: str, topic: str, xp_delta: int, mastery_delta: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == username).first()
    next_suggestions = []
    
    if player:
        player.xp += xp_delta
        player.level = 1 + player.xp // 100
        
        progress = db.query(TopicProgress).filter(
            TopicProgress.player_id == player.id, 
            TopicProgress.topic_name == topic
        ).first()

        completed_just_now = False

        if not progress:
            # Create new if doesn't exist (edge case)
            progress = TopicProgress(player_id=player.id, topic_name=topic, mastery_score=0)
            db.add(progress)

        progress.mastery_score = min(100, progress.mastery_score + mastery_delta)
        
        # Mark visited/current node if topic matches a graph node? 
        # Currently "topic" in API is usually "Math 10" or "Solids".
        # We need to assume 'topic' maps to a node path or label.
        # Ideally frontend sends the NODE_ID (Path). 
        # But for now, let's assume topic is the "label" or "key".
        # We will try to update 'current_node' and 'completed_nodes'
        
        # Check completeness
        if progress.mastery_score >= 100:
            if progress.status != "COMPLETED":
                progress.status = "COMPLETED"
                completed_just_now = True
            
            # Add to completed_nodes list if not present
            # We assume 'topic' is the node identifier being tracked
            current_completed = list(progress.completed_nodes) if progress.completed_nodes else []
            if topic not in current_completed:
                current_completed.append(topic)
                progress.completed_nodes = current_completed
                
        elif progress.status == "NOT_STARTED":
            progress.status = "IN_PROGRESS"
            
        progress.current_node = topic
        db.commit() # Commit updates
        
        # Calculate Next Node if Completed
        if completed_just_now:
            completed_list = list(progress.completed_nodes) if progress.completed_nodes else [topic]
            # Use Grade Level from Player
            suggestions = navigator.get_next_options(completed_list, player.grade_level)
            
            # Logic: If 1 suggestion, auto-assign?
            # User said: "If multiple edges... ask." -> Return list.
            # If one path -> "select next node".
            
            # We will return this in the response so Frontend can handle it.
            next_suggestions = suggestions

    return {"status": "ok", "next_nodes": next_suggestions}

@app.post("/init_session", response_model=InitSessionResponse)
async def init_session(request: InitSessionRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        # New player always saves
        player = Player(
            username=request.username, 
            grade_level=request.grade_level,
            location=request.location,
            learning_style=request.learning_style,
            sex=request.sex,
            birthday=request.birthday,
            interests=request.interests,
            role=request.role
        )
        db.add(player)
        db.commit()
    else:
        # Update existing ONLY if requested
        if request.save_profile:
            player.grade_level = request.grade_level
            player.location = request.location
            player.learning_style = request.learning_style
            if request.sex: player.sex = request.sex
            if request.birthday: player.birthday = request.birthday
            if request.interests: player.interests = request.interests
            if request.role: player.role = request.role
            db.commit()
    
    db.refresh(player)
    
    # CRITICAL: Return the REQUESTED grade level for this session, 
    # even if we didn't save it to the DB.
    # If save_profile is False, player.grade_level might be old (e.g. 3), 
    # but we want to return request.grade_level (e.g. 5) for this session.
    effective_grade = request.grade_level 
    
    return InitSessionResponse(status="ok", username=player.username, grade_level=effective_grade)

@app.post("/resume_shelf", response_model=ResumeShelfResponse)
async def resume_shelf(request: ResumeShelfRequest, db: Session = Depends(get_db)):
    print(f"[API] resume_shelf request for user: '{request.username}' category: '{request.shelf_category}'")
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
         print(f"[API] Player '{request.username}' NOT FOUND in DB.")
         raise HTTPException(status_code=404, detail="Player not found")
         
    # Logic: 
    # 1. Check for Active Node (IN_PROGRESS)
    # 2. If none, check for Next Node recommendations based on completed history.
    
    query = db.query(TopicProgress).filter(TopicProgress.player_id == player.id)
    if request.shelf_category:
        query = query.filter(TopicProgress.topic_name.like(f"{request.shelf_category}%"))
    
    # Check for IN_PROGRESS
    active_progress = query.filter(TopicProgress.status == "IN_PROGRESS").order_by(TopicProgress.mastery_score.desc()).first()
    
    if active_progress:
         return ResumeShelfResponse(topic=active_progress.topic_name, reason=f"Resuming {active_progress.topic_name}...")

    # If no active progress, use Graph Logic to find next
    # We need ALL completed nodes for this player/category to traverse efficiently?
    # Or just use the 'last modified' progress entry to find where they left off.
    
    last_completed = query.filter(TopicProgress.status == "COMPLETED").order_by(TopicProgress.id.desc()).first()
    
    target_topic = ""
    reason = ""

    if last_completed:
        # Use Navigator
        completed_nodes = list(last_completed.completed_nodes) if last_completed.completed_nodes else []
        options = navigator.get_next_options(completed_nodes, player.grade_level)
        
        if not options:
            reason = "Curriculum complete!"
            target_topic = request.shelf_category if request.shelf_category else "Review"
        elif len(options) == 1:
            target_topic = request.shelf_category if request.shelf_category else options[0].split("->")[0] 
            # Fallback split if no category known, though risky. 
            # Better: Since we filtered by cat, use cat.
            if request.shelf_category:
                target_topic = request.shelf_category
            reason = f"Next logical topic: {options[0]}"
        else:
            # Multiple options. WE MUST ASK USER.
            # But resume_shelf returns a single 'topic'.
            # We can return a special string or let Frontend handle it?
            # User requirement: "ask the student to pick one".
            # Hack: return first one but with specific reason?
            # Better: Return "CHOOSE_TOPIC" and let standard Chat/UI handle choice?
            # For now, pick first and note choice.
            if request.shelf_category:
                target_topic = request.shelf_category
            else:
                 target_topic = options[0] # Fallback
            
            reason = f"Suggested next topic: {options[0]}"
    else:
        # Start fresh
        cat = request.shelf_category if request.shelf_category else "Science" # Default
        # Get roots
        options = navigator.get_next_options([], player.grade_level, subject_filter=cat)
        if options:
            target_topic = cat
            reason = f"Starting {cat} curriculum: {options[0]}"
        else:
            target_topic = cat
            reason = "Default start."

    return ResumeShelfResponse(topic=target_topic, reason=reason)
@app.post("/get_topic_graph", response_model=GraphDataResponse)
async def get_topic_graph(request: GraphDataRequest, db: Session = Depends(get_db)):
    from .knowledge_graph import get_graph
    
    kg = get_graph(request.topic)
    if not kg or not kg.graph.nodes:
         return GraphDataResponse(nodes=[])
         
    # Get Player Progress
    player = db.query(Player).filter(Player.username == request.username).first()
    completed_set = set()
    current_node_id = ""
    
    if player:
        # Determine strict subject name (e.g. "math" -> "Math") via TopicProgress usually requiring capitalization
        # But our DB search handles that if we use request.topic directly (assuming UI sends correct case)
        # Or search robustly.
        prog = db.query(TopicProgress).filter(
            TopicProgress.player_id == player.id,
            TopicProgress.topic_name == request.topic
        ).first()
        
        if prog:
            if prog.completed_nodes:
                completed_set = set(prog.completed_nodes)
            if prog.current_node:
                current_node_id = prog.current_node
    
    # Build Node List
    result_nodes = []
    
    # We want to traverse in a logical order if possible, or just dump all and let UI tree sort?
    # UI in Godot will receive a list. It needs to know hierarchy.
    # We have Parent info in node_map in Navigator, but here we use KG graph.
    # KG graph has edges Parent->Child.
    
    # Access internal graph data to get type/parent
    for node_id in kg.graph.nodes():
        node_data = kg.graph.nodes[node_id]
        
        # Determine Status
        status = "locked"
        if node_id in completed_set:
            status = "completed"
        elif node_id == current_node_id:
            status = "current"
        else:
             # Check if available?
             # Simple heuristic: If parent is unlocked?
             # For now, default to locked unless completed.
             # Actually, if we want "Available" vs "Locked", we need `get_next_learnable`.
             pass
             
        # Parents: Find incoming edge from a non-concept node (Topic/Subtopic)
        # KG graph is generic DiGraph.
        parent_id = None
        for pred in kg.graph.predecessors(node_id):
            if kg.graph.nodes[pred].get("type") in ["topic", "subtopic"]:
                parent_id = pred
                break
        
        # If no parent found via graph (Root), it is None
        
        # Check availability roughly if not completed
        if status == "locked":
             # If parent is completed OR parent is root?
             # Simplify: Open if it is a learnable candidate
             pass

        result_nodes.append(GraphNode(
            id=node_id,
            label=node_data.get("label", node_id),
            grade_level=node_data.get("grade_level", 0),
            type=node_data.get("type", "concept"),
            status=status,
            parent=parent_id
        ))
    
    # Late pass for "Available"? 
    # Calling get_next_learnable_nodes is expensive if we do it for all?
    # Just do it once.
    candidates = kg.get_next_learnable_nodes(list(completed_set))
    candidate_ids = set([c.id for c in candidates])
    
    for n in result_nodes:
        if n.status == "locked" and n.id in candidate_ids:
            n.status = "available"
            
    return GraphDataResponse(nodes=result_nodes)

@app.post("/set_current_node")
async def set_current_node(request: SetCurrentNodeRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
        
    prog = db.query(TopicProgress).filter(
        TopicProgress.player_id == player.id,
        TopicProgress.topic_name == request.topic
    ).first()
    
    if not prog:
        # Should create?
        prog = TopicProgress(player_id=player.id, topic_name=request.topic, mastery_score=0)
        db.add(prog)
        
    # Verify node exists in graph?
    # Assume frontend sends valid ID.
    
    prog.current_node = request.node_id
    if prog.status == "NOT_STARTED":
        prog.status = "IN_PROGRESS"
        
    db.commit()
    return {"status": "ok", "current_node": request.node_id}
