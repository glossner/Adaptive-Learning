from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .models import InitRequest, ChatRequest, ChatResponse
from .graph import create_graph
import uuid

# Global graph instance
graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph
    checkpointer = MemorySaver()
    builder = create_graph()
    graph = builder.compile(checkpointer=checkpointer)
    print("Graph compiled with MemorySaver.")
    yield
    print("Shutting down.")

app = FastAPI(lifespan=lifespan)

@app.post("/init")
async def init_session(request: InitRequest):
    # Create thread config
    # structure session_id to be unique
    session_id = str(uuid.uuid4())
    
    initial_state = {
        "topic": request.topic,
        "grade_level": request.grade_level,
        "messages": [], # Start empty
        "current_action": "IDLE",
        "next_dest": "GENERAL_CHAT"
    }
    
    config = {"configurable": {"thread_id": session_id}}
    
    # Update the state with initial values
    await graph.aupdate_state(config, initial_state)
    
    return {"session_id": session_id, "message": f"Session initialized. Topic: {request.topic}"}

@app.post("/chat")
async def chat(request: ChatRequest):
    config = {"configurable": {"thread_id": request.session_id}}
    
    # Check state existence
    current_state = await graph.aget_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Session not found. Please call /init first.")
    
    inputs = {"messages": [HumanMessage(content=request.message)]}
    
    # Run the graph
    # We iterate to complete execution
    result = await graph.ainvoke(inputs, config)
    
    # Result contains the final state values
    messages = result.get("messages", [])
    last_msg = messages[-1].content if messages else ""
    current_action = result.get("current_action", "IDLE")
    
    return ChatResponse(
        response=str(last_msg),
        state_snapshot={"current_action": current_action}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
