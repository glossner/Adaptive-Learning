from fastapi import FastAPI, HTTPException, Depends, Form
from typing import List
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage
from .models import InitRequest, ChatRequest, ChatResponse, BookSelectRequest, BookSelectResponse, InitSessionRequest, InitSessionResponse, ResumeShelfRequest, ResumeShelfResponse, PlayerStatsRequest, GraphDataRequest, GraphDataResponse, GraphNode, SetCurrentNodeRequest, RegisterRequest, LoginRequest, PasswordResetRequest
from .graph import create_graph
from .database import init_db, get_db, Player, TopicProgress
import uuid
import json
from passlib.context import CryptContext
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Auth Setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# IMPORTANT: In production, this must be set via environment variable.
# We default to a placeholder for local dev but advise handling this carefully.
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_me") 
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_reset_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Real Email Sender (IONOS SMTP)
# Real Email Sender (IONOS SMTP)
def send_email_reset_link(to_email: str, link: str):
    # Retrieve config from Environment Variables. No hardcoded defaults for security.
    smtp_server = os.getenv("EMAIL_HOST") 
    smtp_port_str = os.getenv("EMAIL_PORT", "587")
    sender_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    
    # Check if critical vars are present
    if not smtp_server or not sender_email or not password:
        print("[SMTP] EMAIL_HOST/USER/PASSWORD not set. Falling back to Mock.")
        send_email_mock(to_email, link)
        return

    smtp_port = int(smtp_port_str)
    
    if not password:
        print("[SMTP] No EMAIL_PASSWORD set. Falling back to Mock.")
        send_email_mock(to_email, link)
        return

    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "Password Reset Request - Adaptive Tutor"
        message["From"] = sender_email
        message["To"] = to_email

        text = f"""\
Hi,

You requested a password reset for Adaptive Tutor.
Please click the link below to set a new password:

{link}

If you did not request this, please ignore this email.
"""
        html = f"""\
<html>
  <body>
    <p>Hi,</p>
    <p>You requested a password reset for <b>Adaptive Tutor</b>.</p>
    <p>Please click the link below to set a new password:</p>
    <p><a href="{link}">Reset Password</a></p>
    <br>
    <p>If you did not request this, please ignore this email.</p>
  </body>
</html>
"""

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")
        message.attach(part1)
        message.attach(part2)

        context = ssl.create_default_context()
        print(f"[SMTP] Connecting to {smtp_server}:{smtp_port}...")
        
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, message.as_string())
            
        print(f"[SMTP] Email sent successfully to {to_email}")

    except Exception as e:
        print(f"[SMTP] Error sending email: {e}")
        # Build robustness: fall back to printing link so user isn't stuck during testing
        send_email_mock(to_email, link)

# Mock Email Sender (Fallback)
def send_email_mock(email: str, link: str):
    print(f"\n[MOCK EMAIL SERVICE] To: {email}")
    print(f"Subject: Password Reset Request")
    print(f"Body: Click here to reset your password: {link}\n")

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

# Auth Configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # Extended to 60 as requested

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Player).filter(Player.username == username).first()
    if user is None:
        raise credentials_exception
    return user

@app.api_route("/", methods=["GET", "HEAD"])
async def root():
    return {"status": "ok", "message": "Adaptive Learning Backend is running"}

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
    stats["role"] = player.role # [NEW]
        
    return {"stats": stats}

@app.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    print(f"[API] /register request received for: {request.username}")
    # Check if user exists
    existing = db.query(Player).filter(Player.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
        
    hashed_pwd = get_password_hash(request.password)
    
    player = Player(
        username=request.username,
        password_hash=hashed_pwd,
        email=request.email, # [NEW]
        grade_level=request.grade_level,
        location=request.location,
        learning_style=request.learning_style,
        sex=request.sex,
        role=request.role,
        birthday=request.birthday,
        interests=request.interests
    )
    db.add(player)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/request-password-reset")
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player or not player.email:
        # Don't reveal if user exists? For internal app usually mostly fine, but best practice is generic message.
        # "If user exists, email sent".
        return {"message": "If username exists with an email, a reset link has been sent."}
    
    token = create_reset_token({"sub": player.username})
    reset_link = f"http://127.0.0.1:8000/reset-password?token={token}" 
    # NOTE: Fix URL for PROD later (use Host header or config)
    # Check if PROD env var exists to build correct link?
    # For now local is fine, user will likely configure a domain later.
    
    # Use SMTP
    send_email_reset_link(player.email, reset_link)
    
    return {"message": "If username exists with an email, a reset link has been sent."}

@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_form(token: str):
    # Serve Simple HTML Form
    return f"""
    <html>
        <head>
            <title>Reset Password</title>
            <style>
                body {{ font-family: sans-serif; max-width: 400px; margin: 40px auto; padding: 20px; }}
                input {{ width: 100%; padding: 10px; margin-bottom: 10px; }}
                button {{ width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }}
            </style>
        </head>
        <body>
            <h2>Reset Password</h2>
            <form action="/reset-password-confirm" method="post">
                <input type="hidden" name="token" value="{token}">
                <input type="password" name="new_password" placeholder="New Password" required>
                <button type="submit">Reset Password</button>
            </form>
        </body>
    </html>
    """

@app.post("/reset-password-confirm")
async def reset_password_confirm(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    from fastapi import Form
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
             raise HTTPException(status_code=400, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid token")
        
    player = db.query(Player).filter(Player.username == username).first()
    if not player:
        raise HTTPException(status_code=404, detail="User not found")
        
    player.password_hash = get_password_hash(new_password)
    db.commit()
    
    return HTMLResponse(content="<h2>Password Reset Successful</h2><p>You can now return to the app and login.</p>")

@app.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.username == request.username).first()
    if not player:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if not player.password_hash:
        # Legacy user without password - Allow login or reject?
        # For security, we should reject or require update.
        # But for dev/legacy overlap, maybe allow if dev?
        # User requested strict password support for Render.
        # We will reject and say "Legacy Account - Please Reset" (or just fail for now)
        # Actually, let's treat null password as 'allow any' ONLY for localhost? 
        # No, better to be strict.
        pass
        
    if not verify_password(request.password, player.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": player.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/select_book", response_model=BookSelectResponse)
async def select_book(request: BookSelectRequest, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
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
        "currrent_action": "IDLE",
        "last_problem": "",
        "next_dest": "GENERAL_CHAT",
        "role": player.role, # [NEW]
        "view_as_student": False # Default
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
        state_snapshot=state_snapshot,
        role=player.role # [NEW]
    )

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
    config = {"configurable": {"thread_id": request.session_id}}
    
    current_state = await graph.aget_state(config)
    if not current_state.values:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    inputs = {
        "messages": [HumanMessage(content=request.message)],
        "view_as_student": request.view_as_student # [NEW]
    }
    
    if request.grade_override is not None:
        inputs["grade_level"] = f"Grade {request.grade_override}"
        print(f"[API] Grade Override Applied: {inputs['grade_level']}")

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
                    from .knowledge_graph import get_graph
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
async def update_progress(username: str, topic: str, xp_delta: int, mastery_delta: int, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
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
async def init_session(request: InitSessionRequest, current_user: Player = Depends(get_current_user), db: Session = Depends(get_db)):
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

if __name__ == "__main__":
    import uvicorn
    # Use PORT env var or default to 8000
    port = int(os.environ.get("PORT", 8000))
    # Bind to 0.0.0.0 for external access (Render)
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
