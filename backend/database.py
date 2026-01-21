from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import datetime

URL_DATABASE = "sqlite:///./learning_data.db"

engine = create_engine(URL_DATABASE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    location = Column(String, default="New Hampshire")
    grade_level = Column(Integer, default=10) # 0=K, 1-12, 13-16=College, 17+=Masters
    learning_style = Column(String, default="Visual") # Visual, Text, audit, etc
    
    progress = relationship("TopicProgress", back_populates="player")

class TopicProgress(Base):
    __tablename__ = "topic_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    topic_name = Column(String, index=True)
    status = Column(String, default="NOT_STARTED") # NOT_STARTED, IN_PROGRESS, COMPLETED
    mastery_score = Column(Integer, default=0) # 0-100
    mistakes = Column(JSON, default=list) # List of strings (concepts/problems)
    last_state_snapshot = Column(JSON, nullable=True) # Full graph state dump
    
    player = relationship("Player", back_populates="progress")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    username = Column(String, index=True)
    subject = Column(String, index=True) # e.g. "Math", "Science"
    user_query = Column(Text, nullable=True)
    agent_response = Column(Text)
    source_node = Column(String) # "teacher", "verifier", etc.

def init_db():
    Base.metadata.create_all(bind=engine)

def add_mistake(username: str, topic: str, mistake_info: str):
    db: Session = SessionLocal()
    try:
        player = db.query(Player).filter(Player.username == username).first()
        if player:
            progress = db.query(TopicProgress).filter(
                TopicProgress.player_id == player.id, 
                TopicProgress.topic_name == topic
            ).first()
            if progress:
                current_mistakes = list(progress.mistakes) if progress.mistakes else []
                current_mistakes.append(mistake_info)
                progress.mistakes = current_mistakes # Reassign to trigger update
                db.commit()
    except Exception as e:
        print(f"DB Error (add_mistake): {e}")
    finally:
        db.close()

def get_mistakes(username: str, topic: str):
    db: Session = SessionLocal()
    try:
        player = db.query(Player).filter(Player.username == username).first()
        if player:
            progress = db.query(TopicProgress).filter(
                TopicProgress.player_id == player.id, 
                TopicProgress.topic_name == topic
            ).first()
            if progress and progress.mistakes:
                return list(progress.mistakes)
    except Exception as e:
        print(f"DB Error (get_mistakes): {e}")
    return []

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def update_player_progress(username: str, topic: str, xp_delta: int, mastery_delta: int):
    db: Session = SessionLocal()
    try:
        player = db.query(Player).filter(Player.username == username).first()
        if player:
            player.xp += xp_delta
            player.level = 1 + player.xp // 100
            
            progress = db.query(TopicProgress).filter(
                TopicProgress.player_id == player.id, 
                TopicProgress.topic_name == topic
            ).first()
            
            if not progress:
                 progress = TopicProgress(player_id=player.id, topic_name=topic, mastery_score=0)
                 db.add(progress)
            
            progress.mastery_score = min(100, max(0, progress.mastery_score + mastery_delta))
            
            if progress.mastery_score >= 100:
                progress.status = "COMPLETED"
            elif progress.status == "NOT_STARTED" and progress.mastery_score > 0:
                progress.status = "IN_PROGRESS"
                
            db.commit()
            return progress.mastery_score
        return -1
    except Exception as e:
        print(f"DB Error: {e}")
        db.rollback()
        return -1
    finally:
        db.close()

def log_interaction(username: str, subject: str, user_query: str, agent_response: str, source_node: str):
    db: Session = SessionLocal()
    try:
        interaction = Interaction(
            username=username,
            subject=subject,
            user_query=user_query,
            agent_response=agent_response,
            source_node=source_node
        )
        db.add(interaction)
        db.commit()
    except Exception as e:
        print(f"DB Error (log_interaction): {e}")
    finally:
        db.close()

def get_all_users():
    db: Session = SessionLocal()
    try:
        users = db.query(Player.username).all()
        return [u[0] for u in users]
    except Exception as e:
        print(f"DB Error (get_all_users): {e}")
        return []
    finally:
        db.close()
