from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .models import InitRequest, ChatRequest, ChatResponse, BookSelectRequest, BookSelectResponse
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
        player = Player(username=request.username)
        db.add(player)
        db.commit()
        db.refresh(player)
    
    # 2. Get or Create Topic Progress
    progress = db.query(TopicProgress).filter(
        TopicProgress.player_id == player.id,
        TopicProgress.topic_name == request.topic
    ).first()
    
    resume_summary = None
    if not progress:
        progress = TopicProgress(player_id=player.id, topic_name=request.topic)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    else:
        # If exists, we might load state. 
        # For now with MemorySaver and simplified setup, we'll start a fresh 'session' 
        # but inject the known mastery/status.
        resume_summary = f"Continuing {request.topic}. Mastery: {progress.mastery_score}%"

    # 3. Initialize Graph Session
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}
    
    initial_state = {
        "topic": request.topic,
        "grade_level": "Grade 10", # Default for now, could be stored in Player
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
        history_summary=resume_summary
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
    
    # Hook for Gamification: If correct answer (Verifier node logic needed to signal this effectively)
    # For now, we simulate simple XP gain on every interaction to demonstrate persistence.
    # In production, we'd check if 'verifier' praised the user in the state.
    
    # We need to map session_id back to a user/topic (usually via cache or DB lookup of session)
    # Simplified: We won't update DB here to avoid complexity in this snippet 
    # unless we store session_id -> player_id mapping. 
    # We will trust the client to refetch /select_book to see updated stats, 
    # or add an /update_progress endpoint.
    
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

