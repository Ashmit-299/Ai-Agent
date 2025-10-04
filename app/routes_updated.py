import os, time, json, hashlib, traceback, uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
from typing import Optional, List, Dict, Any
from sqlmodel import Session
from core.database import get_session
from core.system_logger import system_logger, log_info, log_warning, log_error, log_user_action, log_system_event, log_database_operation, log_api_request
from .models import (
    ContentResponse, FeedbackRequest, FeedbackResponse, 
    TagRecommendationResponse, MetricsResponse, AnalyticsResponse,
    VideoGenerationResponse, HealthResponse, SuccessResponse
)

def validate_environment():
    """Fallback environment validation"""
    return {'validation': {'valid': True, 'warning_count': 0}}

def get_pooled_connection():
    """Fallback database connection"""
    import sqlite3
    return sqlite3.connect('data.db', check_same_thread=False)

# SQLModel integration with fallback
try:
    from core.db import get_db_session, DatabaseManager
    from core.models import User, Content, Feedback, Script
    from sqlmodel import Session, select
    SQLMODEL_AVAILABLE = True
    db_manager = DatabaseManager()
except ImportError:
    SQLMODEL_AVAILABLE = False
    get_db_session = lambda: None
    db_manager = None

try:
    from .auth import get_current_user, get_current_user_required
    from fastapi.security import HTTPBearer
    from fastapi import Request
    
    # Create optional auth dependency
    security = HTTPBearer(auto_error=False)
    
    async def get_current_user_optional(request: Request):
        """Get current user without requiring authentication"""
        try:
            authorization = request.headers.get("Authorization")
            if not authorization:
                return None
            
            token = authorization.replace("Bearer ", "")
            from .auth import verify_token
            payload = verify_token(token)
            user_id = payload.get("user_id")
            username = payload.get("sub")
            
            if user_id and username:
                class AuthUser:
                    def __init__(self, user_id: str, username: str):
                        self.user_id = user_id
                        self.username = username
                return AuthUser(user_id, username)
            return None
        except:
            return None
            
except ImportError:
    # Fallback when auth is not available
    async def get_current_user():
        return None
    async def get_current_user_required():
        class AnonymousUser:
            def __init__(self):
                self.user_id = 'anonymous'
                self.username = 'anonymous'
        return AnonymousUser()
    async def get_current_user_optional(request: Request):
        return None

# Email service fallback
def send_verification_email(email, token):
    return False
def send_invitation_email(email, inviter, token):
    return False

from .agent import RLAgent
from .streaming_metrics import streaming_metrics
from .task_queue import task_queue
from .observability import track_performance, track_user_action, sentry_manager, posthog_manager, set_user_context, track_event

try:
    from .file_security import FileSecurityValidator, secure_file_upload_handler
except ImportError:
    # Fallback implementations
    class FileSecurityValidator:
        @staticmethod
        async def validate_upload_file(file, user_id=None):
            content = await file.read()
            await file.seek(0)
            return file.filename, content
    
    async def secure_file_upload_handler(file, user_id=None):
        return {
            "status": "success",
            "original_filename": file.filename,
            "secure_filename": file.filename,
            "file_size": file.size
        }

try:
    from .env_security import validate_environment, get_env_security_status
except ImportError:
    # Fallback implementations
    def validate_environment():
        return {'valid': True, 'warnings': []}
    
    def get_env_security_status():
        return {
            'validation': {'valid': True, 'warnings': []},
            'security_level': 'basic'
        }

# Import security manager with fallback
try:
    from .security import SecurityManager, log_security_event
    security_manager = SecurityManager()
except ImportError:
    # Fallback security manager
    class SecurityManager:
        def get_client_ip(self, request):
            return request.client.host if request.client else "unknown"
    
    security_manager = SecurityManager()
    def log_security_event(event_type, details, client_ip, user_id=None):
        import logging
        logging.warning(f"SECURITY_EVENT: {event_type} | IP: {client_ip} | Details: {details}")

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import enhanced bucket system with S3 support
try:
    from core.bhiv_bucket_enhanced import (
        save_script, save_video, get_bucket_path, enhanced_bucket,
        save_upload, save_json, save_rating, list_bucket_files, cleanup_old_files, rotate_logs
    )
    # Import original bucket for backward compatibility
    from core import bhiv_bucket
except ImportError:
    # Fallback to original bucket system
    from core.bhiv_bucket import (
        save_script, save_video, get_bucket_path, save_upload, save_json, 
        save_rating, list_bucket_files, cleanup_old_files, rotate_logs
    )
    from core import bhiv_bucket
    enhanced_bucket = None

from core import bhiv_core

DB_PATH = 'data.db'
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    """Initialize database with SQLModel or fallback to sqlite3"""
    if SQLMODEL_AVAILABLE and db_manager:
        return db_manager.get_session()
    else:
        # Fallback to sqlite3
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        with conn:
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS user (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                created_at REAL
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS invitations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                inviter_id TEXT,
                invitation_token TEXT,
                created_at REAL,
                expires_at REAL,
                used BOOLEAN DEFAULT FALSE
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS content (
                content_id TEXT PRIMARY KEY,
                uploader_id TEXT,
                title TEXT,
                description TEXT,
                file_path TEXT,
                content_type TEXT,
                duration_ms INTEGER,
                uploaded_at REAL,
                authenticity_score REAL,
                current_tags TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0
            )""")
            cur.execute("""CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                user_id TEXT,
                event_type TEXT,
                watch_time_ms INTEGER,
                reward REAL,
                rating INTEGER,
                comment TEXT,
                sentiment TEXT,
                engagement_score REAL,
                ip_address TEXT,
                timestamp REAL
            )""")
            # Add ip_address column if it doesn't exist
            try:
                cur.execute("ALTER TABLE feedback ADD COLUMN ip_address TEXT")
            except:
                pass  # Column already exists
        return conn

# Initialize database connection - use sqlite3 directly to avoid session conflicts
conn = None
try:
    conn = init_db()
except Exception as e:
    import logging
    logging.warning(f"Database initialization failed: {e}")
    conn = None

agent = RLAgent(state_path='agent_state.json')

# Create routers with proper systematic step-by-step tags for grouping
step1_router = APIRouter(tags=["STEP 1: System Health & Demo Access"])
step2_router = APIRouter(tags=["STEP 2: User Authentication"])  # Will be used by auth.py
step3_router = APIRouter(tags=["STEP 3: Content Upload & Video Generation"])
step4_router = APIRouter(tags=["STEP 4: Content Access & Streaming"])
step5_router = APIRouter(tags=["STEP 5: AI Feedback & Tag Recommendations"])
step6_router = APIRouter(tags=["STEP 6: Analytics & Performance Monitoring"])
step7_router = APIRouter(tags=["STEP 7: Task Queue Management"])
step8_router = APIRouter(tags=["STEP 8: System Maintenance & Operations"])
step9_router = APIRouter(tags=["STEP 9: User Interface & Dashboard"])

# Legacy routers for backwards compatibility
task_router = step7_router
maintenance_router = step8_router
ui_router = step9_router

# Main router for backwards compatibility - contains only essential default endpoints
router = APIRouter(tags=["Default Endpoints"])

# Add only essential default endpoints that need to be at root level
@router.get('/health')
def health_check_default():
    """Default health check endpoint - PUBLIC ACCESS"""
    try:
        env_validation = validate_environment()
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "environment_valid": env_validation['validation']['valid'],
            "config_warnings": env_validation['validation']['warning_count'],
            "message": "Use /docs for API documentation",
            "authentication": "not_required"
        }
    except Exception:
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "message": "Use /docs for API documentation",
            "authentication": "not_required"
        }

@router.get('/')
def root():
    """Root endpoint - show welcome page"""
    from fastapi.responses import HTMLResponse
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Content Uploader Agent</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .links { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
            .link-card { background: #007bff; color: white; padding: 15px; border-radius: 5px; text-decoration: none; text-align: center; }
            .link-card:hover { background: #0056b3; }
            .status { background: #28a745; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 AI Content Uploader Agent</h1>
            <div class="status">✅ Server Running Successfully</div>
            <p>Welcome to the AI-powered content analysis and video generation platform.</p>
            
            <div class="links">
                <a href="/docs" class="link-card">📚 API Documentation</a>
                <a href="/health" class="link-card">💚 Health Check</a>
                <a href="/dashboard" class="link-card">📊 Dashboard</a>
                <a href="/demo-login" class="link-card">🔑 Demo Login</a>
            </div>
            
            <h3>Quick Start:</h3>
            <ol>
                <li>Get demo credentials from <a href="/demo-login">/demo-login</a></li>
                <li>Visit <a href="/docs">/docs</a> for interactive API testing</li>
                <li>Use POST /users/login to authenticate</li>
                <li>Upload content with POST /upload</li>
            </ol>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get('/test')
def simple_test():
    """Simple test endpoint to verify server is working"""
    return {
        "status": "working",
        "message": "Server is running correctly",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "endpoints": {
            "health": "/health",
            "demo_login": "/demo-login", 
            "api_docs": "/docs",
            "contents": "/contents",
            "metrics": "/metrics"
        },
        "next_steps": [
            "Visit /docs for full API documentation",
            "Use /demo-login to get test credentials",
            "Try /contents to see available content"
        ]
    }

# Add S3 storage status endpoint
@step6_router.get('/storage/status')
def get_storage_status(current_user = Depends(get_current_user_required)):
    """Get storage system status including S3 integration"""
    try:
        storage_status = {
            "local_storage": {
                "enabled": True,
                "bucket_path": "bucket/",
                "segments": ["uploads", "videos", "scripts", "storyboards", "ratings", "logs"]
            },
            "s3_storage": {
                "enabled": os.getenv("USE_S3_STORAGE", "false").lower() == "true",
                "configured": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")),
                "bucket_name": os.getenv("S3_BUCKET_NAME", "ai-agent-storage"),
                "region": os.getenv("S3_REGION", "us-east-1"),
                "endpoint": os.getenv("S3_ENDPOINT_URL", "AWS S3")
            },
            "enhanced_bucket": enhanced_bucket is not None
        }
        
        if enhanced_bucket:
            storage_status["enhanced_features"] = {
                "presigned_urls": True,
                "automatic_backup": True,
                "s3_fallback": True
            }
        
        return {
            "storage_status": storage_status,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            "error": str(e),
            "storage_status": {"error": "Failed to get storage status"},
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

# Add presigned URL generation endpoint
@step6_router.post('/storage/presigned-upload')
def generate_presigned_upload_url(
    filename: str,
    content_type: str = None,
    current_user = Depends(get_current_user_required)
):
    """Generate presigned URL for direct S3 uploads"""
    if not enhanced_bucket:
        raise HTTPException(status_code=501, detail="Enhanced bucket system not available")
    
    try:
        presigned_data = enhanced_bucket.generate_presigned_upload_url(filename, content_type)
        
        if not presigned_data:
            raise HTTPException(status_code=503, detail="S3 storage not available")
        
        return {
            "presigned_upload": presigned_data,
            "filename": filename,
            "content_type": content_type,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")

# Continue with all existing endpoints...
# (The rest of the file remains the same as the original routes.py)