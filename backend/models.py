from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class InitRequest(BaseModel):
    user_id: str # This will be the username now
    grade_level: str
    topic: str
    additional_context: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str
    view_as_student: bool = False # Toggle mode
    grade_override: Optional[int] = None # Force content grade level

class ChatResponse(BaseModel):
    response: str
    state_snapshot: Optional[Dict] = None

class BookSelectRequest(BaseModel):
    username: str
    topic: str
    manual_mode: bool = False
    session_grade_level: Optional[int] = None # The grade effective for this session

class BookSelectResponse(BaseModel):
    session_id: str
    status: str
    xp: int
    level: int
    mastery: int
    history_summary: Optional[str] = None
    state_snapshot: Optional[Dict] = None 
    role: Optional[str] = "Student" # To inform UI to show toggle

class InitSessionRequest(BaseModel):
    username: str
    grade_level: int
    location: str
    learning_style: str
    sex: Optional[str] = "Not Specified"
    birthday: Optional[str] = None
    interests: Optional[str] = None
    role: Optional[str] = None
    save_profile: bool = False

class InitSessionResponse(BaseModel):
    status: str
    username: str
    grade_level: int

class ResumeShelfRequest(BaseModel):
    username: str
    shelf_category: str # e.g. "Math" (Optional, if we want to just resume general)

class ResumeShelfResponse(BaseModel):
    topic: str
    reason: str

class PlayerStatsRequest(BaseModel):
    username: str

class GraphDataRequest(BaseModel):
    topic: str
    username: str

class GraphNode(BaseModel):
    id: str
    label: str
    grade_level: int
    type: str # topic, subtopic, concept
    status: str # locked, available, completed, current
    parent: Optional[str] = None

class GraphDataResponse(BaseModel):
    nodes: List[GraphNode]

class SetCurrentNodeRequest(BaseModel):
    username: str
    topic: str
    node_id: str
