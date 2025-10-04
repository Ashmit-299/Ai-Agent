#!/usr/bin/env python3
"""
SQLModel Database Models - Production Ready with Migration Support
"""

from sqlmodel import SQLModel, Field, create_engine, Session, Relationship
from typing import Optional, List
from datetime import datetime
import time
import os

# Database Models with explicit table configurations

class User(SQLModel, table=True):
    __tablename__ = "user"
    
    user_id: str = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: Optional[str] = None
    email: Optional[str] = None
    email_verified: bool = Field(default=False)
    verification_token: Optional[str] = None
    sub: Optional[str] = None  # Supabase user ID
    role: str = Field(default="user")
    last_login: Optional[float] = None
    created_at: float = Field(default_factory=time.time)

class Content(SQLModel, table=True):
    __tablename__ = "content"
    
    content_id: str = Field(primary_key=True)
    uploader_id: str = Field(foreign_key="user.user_id")
    title: str
    description: Optional[str] = None
    file_path: str
    content_type: str
    duration_ms: int = Field(default=0)
    uploaded_at: float = Field(default_factory=time.time)
    authenticity_score: float = Field(default=0.0)
    current_tags: Optional[str] = None  # JSON string
    views: int = Field(default=0)
    likes: int = Field(default=0)
    shares: int = Field(default=0)

class Feedback(SQLModel, table=True):
    __tablename__ = "feedback"
    
    id: Optional[int] = Field(primary_key=True)
    content_id: str = Field(foreign_key="content.content_id")
    user_id: str = Field(foreign_key="user.user_id")
    event_type: str
    watch_time_ms: int = Field(default=0)
    reward: float = Field(default=0.0)
    rating: Optional[int] = None
    comment: Optional[str] = None
    sentiment: Optional[str] = None
    engagement_score: Optional[float] = None
    ip_address: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)

class Script(SQLModel, table=True):
    __tablename__ = "script"
    
    script_id: str = Field(primary_key=True)
    content_id: Optional[str] = Field(default=None, foreign_key="content.content_id")
    user_id: str = Field(foreign_key="user.user_id")
    title: str
    script_content: str
    script_type: Optional[str] = Field(default="text")
    file_path: Optional[str] = Field(default=None)
    created_at: float = Field(default_factory=time.time)
    used_for_generation: bool = Field(default=False)
    version: Optional[str] = Field(default="1.0")
    script_metadata: Optional[str] = Field(default=None)  # JSON string - renamed to avoid conflict

class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None)
    action: str  # upload, rate, conversion, delete, etc.
    resource_type: str  # content, user, script, etc.
    resource_id: str
    timestamp: float = Field(default_factory=time.time)
    ip_address: Optional[str] = Field(default=None)
    user_agent: Optional[str] = Field(default=None)
    request_id: Optional[str] = Field(default=None)
    details: Optional[str] = Field(default=None)  # JSON string
    status: Optional[str] = Field(default="success")

class Invitation(SQLModel, table=True):
    __tablename__ = "invitations"
    
    id: Optional[int] = Field(primary_key=True)
    email: str
    inviter_id: str = Field(foreign_key="user.user_id")
    invitation_token: str = Field(unique=True)
    created_at: float = Field(default_factory=time.time)
    expires_at: float
    used: bool = Field(default=False)
    used_at: Optional[float] = None

class Analytics(SQLModel, table=True):
    __tablename__ = "analytics"
    
    id: Optional[int] = Field(primary_key=True)
    event_type: str
    user_id: Optional[str] = Field(foreign_key="user.user_id")
    content_id: Optional[str] = Field(foreign_key="content.content_id")
    event_data: Optional[str] = None  # JSON string
    timestamp: float = Field(default_factory=time.time)
    ip_address: Optional[str] = None

class SystemLog(SQLModel, table=True):
    __tablename__ = "system_logs"
    
    id: Optional[int] = Field(primary_key=True)
    level: str
    message: str
    module: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)
    user_id: Optional[str] = Field(foreign_key="user.user_id")
    extra_data: Optional[str] = None  # JSON string for additional data
    error_details: Optional[str] = None  # Error message if applicable
    traceback: Optional[str] = None  # Full traceback for errors

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

def get_engine():
    """Get database engine with proper configuration"""
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(
            DATABASE_URL,
            echo=False,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration for production
        return create_engine(
            DATABASE_URL,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10
        )

engine = get_engine()

def create_db_and_tables():
    """Create database tables - Use only for development"""
    try:
        SQLModel.metadata.create_all(engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Table creation failed: {e}")

def get_session():
    """Get database session"""
    with Session(engine) as session:
        yield session