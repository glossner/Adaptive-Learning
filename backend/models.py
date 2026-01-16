from pydantic import BaseModel
from typing import List, Optional, Dict

class InitRequest(BaseModel):
    user_id: str
    grade_level: str
    topic: str
    additional_context: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str
    state_snapshot: Optional[Dict] = None
