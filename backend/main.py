from fastapi import FastAPI, HTTPException, Depends
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
    
    # 3. Adaptive Logic: Check Grade Level
    # Extract number from topic string (e.g. "History 1" -> 1)
    # Simple heuristic: look for last number
    import re
    topic_grade_match = re.search(r'\d+', request.topic)
    if topic_grade_match:
        topic_grade = int(topic_grade_match.group())
        # If student is Grade 10 and picks Grade 1 topic?
        if player.grade_level > topic_grade + 2:
            # Suggest higher level
            suggested_topic = request.topic.replace(str(topic_grade), str(player.grade_level))
            adaptive_suggestion = f"\n\n[System]: You are currently at Grade {player.grade_level}. '{request.topic}' might be too easy. Consider trying '{suggested_topic}' instead."

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
        "grade_level": f"Grade {topic_grade}" if topic_grade_match else f"Grade {player.grade_level}", 
        "location": player.location,
        "learning_style": player.learning_style,
        "messages": [], 
        "current_action": "IDLE",
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
    
    return ChatResponse(
        response=str(last_msg),
        state_snapshot={"current_action": current_action}
    )

@app.post("/update_progress")
async def update_progress(username: str, topic: str, xp_delta: int, mastery_delta: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == username).first()
    if player:
        player.xp += xp_delta
        # simple level up logic
        player.level = 1 + player.xp // 100
        
        progress = db.query(TopicProgress).filter(
            TopicProgress.player_id == player.id, 
            TopicProgress.topic_name == topic
        ).first()
        if progress:
            progress.mastery_score = min(100, progress.mastery_score + mastery_delta)
            if progress.mastery_score >= 100:
                progress.status = "COMPLETED"
            elif progress.status == "NOT_STARTED":
                progress.status = "IN_PROGRESS"
                
        db.commit()
    return {"status": "ok"}

@app.post("/init_session", response_model=InitSessionResponse)
async def init_session(request: InitSessionRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        player = Player(
            username=request.username, 
            grade_level=request.grade_level,
            location=request.location,
            learning_style=request.learning_style
        )
        db.add(player)
    else:
        # Update existing
        player.grade_level = request.grade_level
        player.location = request.location
        player.learning_style = request.learning_style
    
    db.commit()
    db.refresh(player)
    return InitSessionResponse(status="ok", username=player.username, grade_level=player.grade_level)

@app.post("/resume_shelf", response_model=ResumeShelfResponse)
async def resume_shelf(request: ResumeShelfRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
         raise HTTPException(status_code=404, detail="Player not found")
         
    # Logic: Find most recent "IN_PROGRESS" topic matching shelf category if provided
    # Simplified: Just find most recent modified progress
    last_progress = db.query(TopicProgress).filter(
        TopicProgress.player_id == player.id
    ).order_by(TopicProgress.mastery_score.desc()).first() # Hacky: usage based on mastery/updates
    
    # Or just suggest based on Grade
    if last_progress:
        return ResumeShelfResponse(topic=last_progress.topic_name, reason="Resuming your last session.")
    
    # Suggest default
    default = f"Math {player.grade_level}"
    return ResumeShelfResponse(topic=default, reason="Starting new curriculum.")
