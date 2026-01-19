from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

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
    last_state_snapshot = Column(JSON, nullable=True) # Full graph state dump
    
    player = relationship("Player", back_populates="progress")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
