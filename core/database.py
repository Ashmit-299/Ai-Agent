import os
# Fix psycopg2 import issue
try:
    import psycopg2
except ImportError:
    try:
        import psycopg2_binary as psycopg2
        import sys
        sys.modules['psycopg2'] = psycopg2
    except ImportError:
        pass

from sqlmodel import SQLModel, create_engine, Session, select
from .models import User, Content, Feedback
from typing import Optional, List
import json
import time
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")

# Engine configuration for Supabase
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={
        "connect_timeout": 10,
        "sslmode": "require"
    }
)

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Table creation failed: {e}")
        pass  # Tables may already exist

def get_session():
    with Session(engine) as session:
        yield session

class DatabaseManager:
    def __init__(self):
        self.engine = engine
    
    @staticmethod
    def create_user(user_data: dict):
        with Session(engine) as session:
            user = User(**user_data)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
    
    @staticmethod
    def get_user_by_username(username: str):
        with Session(engine) as session:
            statement = select(User).where(User.username == username)
            return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_id(user_id: str):
        with Session(engine) as session:
            statement = select(User).where(User.user_id == user_id)
            return session.exec(statement).first()
    
    @staticmethod
    def create_content(content_data: dict):
        with Session(engine) as session:
            content = Content(**content_data)
            session.add(content)
            session.commit()
            session.refresh(content)
            return content
    
    @staticmethod
    def get_content_by_id(content_id: str):
        with Session(engine) as session:
            statement = select(Content).where(Content.content_id == content_id)
            return session.exec(statement).first()
    
    @staticmethod
    def create_feedback(feedback_data: dict):
        with Session(engine) as session:
            feedback = Feedback(**feedback_data)
            session.add(feedback)
            session.commit()
            session.refresh(feedback)
            return feedback
    
    @staticmethod
    def get_analytics_data() -> dict:
        with Session(engine) as session:
            total_users = len(session.exec(select(User)).all())
            total_content = len(session.exec(select(Content)).all())
            total_feedback = len(session.exec(select(Feedback)).all())
            
            avg_rating = session.exec(
                select(Feedback.rating).where(Feedback.rating.is_not(None))
            ).all()
            avg_rating = sum(avg_rating) / len(avg_rating) if avg_rating else 0
            
            sentiment_counts = {}
            sentiments = session.exec(select(Feedback.sentiment)).all()
            for sentiment in sentiments:
                if sentiment:
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            return {
                "total_users": total_users,
                "total_content": total_content,
                "total_feedback": total_feedback,
                "average_rating": round(avg_rating, 2),
                "sentiment_breakdown": sentiment_counts
            }

# Initialize database
create_db_and_tables()
db = DatabaseManager()