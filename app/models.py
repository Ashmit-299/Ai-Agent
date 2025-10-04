"""Pydantic models for request/response validation"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication Models
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: Optional[str] = Field(None, max_length=255)

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int  # minutes
    user_id: str
    username: str

class RefreshToken(BaseModel):
    refresh_token: str

class PasswordReset(BaseModel):
    email: str = Field(..., max_length=255)

class PasswordChange(BaseModel):
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=8)

class EmailVerification(BaseModel):
    token: str = Field(..., min_length=1)

class User(BaseModel):
    user_id: str
    username: str
    email: Optional[str] = None

# Content Models
class ContentUpload(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field("", max_length=1000)

class ContentResponse(BaseModel):
    content_id: str
    title: str
    description: str
    file_path: str
    content_type: str
    authenticity_score: float
    tags: List[str]
    next_step: str

class ContentList(BaseModel):
    items: List[Dict[str, Any]]
    total_count: int
    next_step: str

# Feedback Models
class FeedbackRequest(BaseModel):
    content_id: str = Field(..., min_length=1, max_length=100)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)

class FeedbackResponse(BaseModel):
    status: str
    rating: int
    event_type: str
    reward: float
    rl_training: Dict[str, Any]
    next_step: str

# Tag Recommendation Models
class TagRecommendationResponse(BaseModel):
    content_id: str
    recommended_tags: List[str]
    original_tags: List[str]
    rl_action_taken: str
    authenticity_score: float
    agent_confidence: Dict[str, Any]
    next_step: str

# Analytics Models
class MetricsResponse(BaseModel):
    system_metrics: Dict[str, int]
    rl_agent_metrics: Dict[str, Any]
    timestamp: str
    next_step: str

class AnalyticsResponse(BaseModel):
    total_users: int
    total_content: int
    total_feedback: int
    average_rating: float
    average_engagement: float
    sentiment_breakdown: Dict[str, int]
    engagement_rate: float
    timestamp: str

# Video Generation Models
class VideoGenerationResponse(BaseModel):
    content_id: str
    video_path: str
    stream_url: str
    local_file_path: str
    storyboard_stats: Dict[str, Any]
    processing_status: str
    next_step: str

# Task Queue Models
class TaskStatus(BaseModel):
    task_id: str
    status: str
    progress: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class QueueStats(BaseModel):
    queue_stats: Dict[str, Any]
    timestamp: str

# Health Check Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    systematic_organization: Optional[str] = None
    environment_valid: Optional[bool] = None
    config_warnings: Optional[int] = None
    next_step: str

# Error Models
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: Optional[str] = None

# Generic Response Models
class SuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: Optional[str] = None
    timestamp: str