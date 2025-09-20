#!/usr/bin/env python3
"""
SQLModel Database Models
"""

from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional, List
from datetime import datetime
import time

class User(SQLModel, table=True, extend_existing=True):
    user_id: str = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = False
    verification_token: Optional[str] = None
    sub: Optional[str] = None  # Supabase user ID
    created_at: float = Field(default_factory=time.time)

class Content(SQLModel, table=True, extend_existing=True):
    content_id: str = Field(primary_key=True)
    uploader_id: str = Field(foreign_key="user.user_id")
    title: str
    description: Optional[str] = None
    file_path: str
    content_type: str
    duration_ms: int = 0
    uploaded_at: float = Field(default_factory=time.time)
    authenticity_score: float = 0.0
    current_tags: Optional[str] = None  # JSON string
    views: int = 0
    likes: int = 0
    shares: int = 0

class Feedback(SQLModel, table=True, extend_existing=True):
    id: Optional[int] = Field(primary_key=True)
    content_id: str = Field(foreign_key="content.content_id")
    user_id: str = Field(foreign_key="user.user_id")
    event_type: str
    watch_time_ms: int = 0
    reward: float = 0.0
    rating: Optional[int] = None
    comment: Optional[str] = None
    sentiment: Optional[str] = None
    engagement_score: Optional[float] = None
    timestamp: float = Field(default_factory=time.time)

# Database engine and session management
DATABASE_URL = "sqlite:///./data.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session