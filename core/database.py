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
from .models import User, Content, Feedback, Script
from typing import Optional, List
import json
import time
from datetime import datetime

# Use SQLite for local development, PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_agent.db")

# Engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10
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
    def create_script(script_data: dict):
        try:
            with Session(engine) as session:
                script = Script(**script_data)
                session.add(script)
                session.commit()
                session.refresh(script)
                return script
        except Exception as e:
            print(f"Script creation failed (table may not exist): {e}")
            return None
    
    @staticmethod
    def get_script_by_id(script_id: str):
        try:
            with Session(engine) as session:
                statement = select(Script).where(Script.script_id == script_id)
                return session.exec(statement).first()
        except Exception as e:
            print(f"Script query failed (table may not exist): {e}")
            return None
    
    @staticmethod
    def get_analytics_data() -> dict:
        with Session(engine) as session:
            try:
                total_users = len(session.exec(select(User)).all())
                total_content = len(session.exec(select(Content)).all())
                total_feedback = len(session.exec(select(Feedback)).all())
                
                # Try to get scripts count, handle if table doesn't exist
                try:
                    total_scripts = len(session.exec(select(Script)).all())
                except Exception:
                    total_scripts = 0
                
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
                    "total_scripts": total_scripts,
                    "average_rating": round(avg_rating, 2),
                    "sentiment_breakdown": sentiment_counts
                }
            except Exception as e:
                # Fallback for database errors
                return {
                    "total_users": 0,
                    "total_content": 0,
                    "total_feedback": 0,
                    "total_scripts": 0,
                    "average_rating": 0.0,
                    "sentiment_breakdown": {},
                    "error": str(e)
                }

# Initialize database
create_db_and_tables()
db = DatabaseManager()