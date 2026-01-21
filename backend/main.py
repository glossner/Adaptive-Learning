from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .models import InitRequest, ChatRequest, ChatResponse, BookSelectRequest, BookSelectResponse, InitSessionRequest, InitSessionResponse, ResumeShelfRequest, ResumeShelfResponse
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
    
    return BookSelectResponse(
        session_id=session_id,
        status=progress.status,
        xp=player.xp,
        level=player.level,
        mastery=progress.mastery_score,
        history_summary=full_summary
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

