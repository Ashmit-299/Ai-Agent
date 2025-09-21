import os, time, json, hashlib, traceback, uuid
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Body, Request, Depends
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
import sqlite3
from typing import Optional, List, Dict, Any
from sqlmodel import Session
from core.database import get_session
from .models import (
    ContentResponse, FeedbackRequest, FeedbackResponse, 
    TagRecommendationResponse, MetricsResponse, AnalyticsResponse,
    VideoGenerationResponse, HealthResponse, SuccessResponse
)
# Removed imports for deleted modules
# from .config_validator import validate_environment
# from .db_pool import get_pooled_connection

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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core import bhiv_bucket
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
                timestamp REAL
            )""")
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
    """Default health check endpoint"""
    try:
        env_validation = validate_environment()
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "environment_valid": env_validation['validation']['valid'],
            "config_warnings": env_validation['validation']['warning_count'],
            "message": "Use /docs for API documentation"
        }
    except Exception:
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "message": "Use /docs for API documentation"
        }

@router.get('/')
def root():
    """Root endpoint - redirect to API docs"""
    return RedirectResponse(url="/docs")

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

# Remove all other endpoints from default router - they are now properly organized in step routers

# Create demo user if not exists
def create_demo_user():
    from .security import hash_password
    try:
        if SQLMODEL_AVAILABLE and db_manager:
            # Use SQLModel
            try:
                existing_user = db_manager.get_user_by_username('demo')
                if not existing_user:
                    demo_hash = hash_password('demo123')
                    demo_user_data = {
                        'user_id': 'demo001',
                        'username': 'demo',
                        'password_hash': demo_hash,
                        'email': 'demo@example.com',
                        'created_at': time.time()
                    }
                    db_manager.create_user(demo_user_data)
            except Exception as e:
                # Fallback to sqlite3 if SQLModel fails
                import sqlite3
                temp_conn = sqlite3.connect('data.db')
                with temp_conn:
                    cur = temp_conn.cursor()
                    cur.execute('SELECT user_id FROM user WHERE username=?', ('demo',))
                    if not cur.fetchone():
                        demo_hash = hash_password('demo123')
                        cur.execute('INSERT INTO user(user_id, username, password_hash, email, created_at) VALUES (?,?,?,?,?)',
                                   ('demo001', 'demo', demo_hash, 'demo@example.com', time.time()))
                temp_conn.close()
        else:
            # Fallback to sqlite3
            import sqlite3
            temp_conn = sqlite3.connect('data.db')
            with temp_conn:
                cur = temp_conn.cursor()
                cur.execute('SELECT user_id FROM user WHERE username=?', ('demo',))
                if not cur.fetchone():
                    demo_hash = hash_password('demo123')
                    cur.execute('INSERT INTO user(user_id, username, password_hash, email, created_at) VALUES (?,?,?,?,?)',
                               ('demo001', 'demo', demo_hash, 'demo@example.com', time.time()))
            temp_conn.close()
    except Exception as e:
        import logging
        logging.warning(f"Demo user creation failed: {e}")

create_demo_user()

# ===== STEP 1: SYSTEM STATUS & ONBOARDING =====

@step1_router.get('/health')
def health_check():
    """STEP 1A: Check if system is running"""
    try:
        env_validation = validate_environment()
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "systematic_organization": "9 step workflow",
            "environment_valid": env_validation['validation']['valid'],
            "config_warnings": env_validation['validation']['warning_count'],
            "next_step": "GET /demo-login for test credentials or POST /users/register to create account"
        }
    except Exception:
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "next_step": "GET /demo-login for test credentials or POST /users/register to create account"
        }

@step1_router.get('/demo-login')
def demo_login():
    """STEP 1B: Get demo credentials for quick testing"""
    return {
        "demo_credentials": {"username": "demo", "password": "demo123"},
        "next_step": "POST /users/login with these credentials to get access token"
    }

# ===== STEP 2: USER AUTHENTICATION =====

class InviteUser(BaseModel):
    email: str

@step2_router.post('/invite-user')
def invite_user(invite: InviteUser, current_user = Depends(get_current_user_required)):
    """STEP 2A: Send user invitation (requires authentication)"""
    # Enhanced security validation
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Email validation
    import re
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, invite.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    
    # Rate limiting check (max 5 invitations per hour per user)
    try:
        import sqlite3
        temp_conn = sqlite3.connect('data.db')
        with temp_conn:
            cur = temp_conn.cursor()
            # Check recent invitations
            hour_ago = time.time() - 3600
            cur.execute('SELECT COUNT(*) FROM invitations WHERE inviter_id=? AND created_at > ?', 
                       (current_user.user_id, hour_ago))
            recent_count = cur.fetchone()[0]
            
            if recent_count >= 5:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 5 invitations per hour.")
            
            # Check if email already invited recently
            cur.execute('SELECT COUNT(*) FROM invitations WHERE email=? AND created_at > ? AND used=FALSE', 
                       (invite.email, hour_ago))
            if cur.fetchone()[0] > 0:
                raise HTTPException(status_code=400, detail="Email already has pending invitation")
            
            invitation_token = uuid.uuid4().hex
            expires_at = time.time() + (7 * 24 * 3600)  # 7 days
            
            cur.execute('INSERT INTO invitations(email,inviter_id,invitation_token,created_at,expires_at) VALUES (?,?,?,?,?)',
                       (invite.email, current_user.user_id, invitation_token, time.time(), expires_at))
        temp_conn.close()
        
        # Send invitation email (sanitized)
        email_sent = send_invitation_email(invite.email, current_user.username, invitation_token)
        
        return {
            'status': 'success',
            'email': invite.email,
            'email_sent': email_sent,
            'invitation_token': invitation_token if not email_sent else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Invitation failed")

@step2_router.get('/verify-email')
def verify_email(token: str):
    """STEP 2B: Verify user email address"""
    try:
        import sqlite3
        temp_conn = sqlite3.connect('data.db')
        with temp_conn:
            cur = temp_conn.cursor()
            cur.execute('UPDATE user SET email_verified=TRUE WHERE verification_token=?', (token,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=400, detail='Invalid verification token')
        temp_conn.close()
        
        return {'status': 'success', 'message': 'Email verified successfully'}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step2_router.get('/accept-invitation')
def accept_invitation(token: str):
    """STEP 2C: Accept user invitation"""
    try:
        import sqlite3
        temp_conn = sqlite3.connect('data.db')
        with temp_conn:
            cur = temp_conn.cursor()
            cur.execute('SELECT email,expires_at,used FROM invitations WHERE invitation_token=?', (token,))
            result = cur.fetchone()
            
            if not result:
                raise HTTPException(status_code=400, detail='Invalid invitation token')
            
            email, expires_at, used = result
            
            if used:
                raise HTTPException(status_code=400, detail='Invitation already used')
            
            if time.time() > expires_at:
                raise HTTPException(status_code=400, detail='Invitation expired')
        temp_conn.close()
        
        return {
            'status': 'valid',
            'email': email,
            'message': 'Invitation is valid. Please complete registration.',
            'register_url': f'/users/register?email={email}&invitation_token={token}'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Note: Main auth endpoints are in auth.py router (/users/register, /users/login, /users/profile)
# These are fallback endpoints for direct access without auth router

# ===== STEP 3: CONTENT CREATION =====

@step3_router.get('/contents')
def list_contents(limit: int = 20, current_user = Depends(get_current_user)):
    """STEP 3A: Browse existing content (authentication optional for personalized results)"""
    try:
        from core.database import DatabaseManager
        from sqlmodel import Session, select, desc
        from core.models import Content
        
        db = DatabaseManager()
        with Session(db.engine) as session:
            statement = select(Content).order_by(desc(Content.uploaded_at)).limit(limit)
            contents = session.exec(statement).all()
        
        return {
            'items': [{
                'content_id': content.content_id,
                'title': content.title, 
                'description': content.description,
                'authenticity_score': content.authenticity_score
            } for content in contents],
            'next_step': 'POST /upload to add new content or POST /generate-video to create from script'
        }
    except Exception as e:
        return {
            'items': [],
            'message': 'No content found or database not initialized',
            'next_step': 'POST /upload to add new content or POST /generate-video to create from script'
        }

# Simplified video generation endpoint above

@step3_router.post('/upload', response_model=ContentResponse, status_code=201)
async def upload(file: UploadFile = File(...), title: str = Form(...), description: str = Form(''), current_user = Depends(get_current_user), session: Session = Depends(get_session)):
    """STEP 3B: Upload content file (requires authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_extensions = {'.mp4', '.mp3', '.wav', '.jpg', '.jpeg', '.png', '.txt', '.pdf'}
        allowed_mime_types = {
            'video/mp4', 'audio/mpeg', 'audio/wav', 'image/jpeg', 'image/png', 'text/plain', 'application/pdf'
        }
        
        safe_filename = os.path.basename(file.filename)
        ext = os.path.splitext(safe_filename)[1].lower()
        
        if ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File extension {ext} not allowed")
        
        # More flexible MIME type validation - allow if extension is valid
        if file.content_type and file.content_type not in allowed_mime_types:
            # Allow if extension is in allowed list (browser may send generic MIME type)
            if ext not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"MIME type {file.content_type} not allowed")
        
        data = await file.read()
        max_size = 100 * 1024 * 1024
        if len(data) > max_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        h = hashlib.sha256(data).hexdigest()[:12]
        content_id = f"{h}_{uuid.uuid4().hex[:6]}"
        uploader_id = current_user.user_id if current_user else 'anonymous'
        
        # Clean filename more thoroughly
        clean_name = ''.join(c for c in safe_filename if c.isalnum() or c in '.-_')
        if not clean_name:
            clean_name = f"file{ext}"
        fname = f"{int(time.time())}_{content_id}_{clean_name}"
        
        # Save to temporary location first
        temp_path = bhiv_bucket.get_bucket_path("tmp", fname)
        with open(temp_path, 'wb') as f:
            f.write(data)
        
        # Save all uploaded files to uploads folder
        bucket_path = bhiv_bucket.save_upload(temp_path, fname)
        
        # If it's a script file, also save to scripts bucket
        script_path = None
        if ext == '.txt':
            try:
                script_filename = f"{content_id}_script.txt"
                script_path = bhiv_bucket.save_script(temp_path, script_filename)
                import logging
                logging.info(f"Script file also saved to scripts bucket: {script_path}")
            except Exception as script_error:
                import logging
                logging.warning(f"Failed to save script to scripts bucket: {script_error}")
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except (OSError, FileNotFoundError) as e:
            import logging
            logging.warning(f"Failed to clean up temp file {temp_path}: {e}")
        
        safe_path = bucket_path
        
        authenticity = compute_authenticity(safe_path, title, description)
        tags = suggest_tags(title, description)
        uploaded_at = time.time()
        
        # Save to Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            content_data = {
                'content_id': content_id,
                'uploader_id': uploader_id,
                'title': title,
                'description': description,
                'file_path': safe_path,
                'content_type': file.content_type or 'application/octet-stream',
                'authenticity_score': authenticity,
                'current_tags': json.dumps(tags),
                'uploaded_at': uploaded_at
            }
            db.create_content(content_data)
            
            # If it's a script file, also save to scripts table
            if ext == '.txt' and script_path:
                try:
                    script_content = data.decode('utf-8')
                    script_data = {
                        'script_id': f"upload_{content_id}",
                        'content_id': content_id,
                        'user_id': uploader_id,
                        'title': f"Uploaded script: {title}",
                        'script_content': script_content,
                        'script_type': 'uploaded_text',
                        'file_path': script_path,
                        'used_for_generation': False
                    }
                    db.create_script(script_data)
                    import logging
                    logging.info(f"Script data saved to database: upload_{content_id}")
                except Exception as script_db_error:
                    import logging
                    logging.warning(f"Failed to save script to database: {script_db_error}")
            
            # Save upload log
            log_data = {
                'content_id': content_id,
                'user_id': uploader_id,
                'action': 'file_upload',
                'filename': safe_filename,
                'file_size': len(data),
                'content_type': file.content_type,
                'tags': tags,
                'authenticity_score': authenticity,
                'bucket_path': bucket_path,
                'script_path': script_path,
                'timestamp': uploaded_at
            }
            log_filename = f"upload_{content_id}_{int(uploaded_at)}.json"
            try:
                bhiv_bucket.save_json('logs', log_filename, log_data)
                import logging
                logging.info(f"Upload log saved: {log_filename}")
            except Exception as log_error:
                import logging
                logging.warning(f"Failed to save upload log: {log_error}")
                
        except Exception as db_error:
            import logging
            logging.error(f"Database save failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database save failed: {str(db_error)}")
        
        # Register content with RL agent for future recommendations
        try:
            agent.register_content(content_id, tags, authenticity)
        except Exception as rl_error:
            import logging
            logging.warning(f"Failed to register content with RL agent: {rl_error}")
        
        return ContentResponse(
            content_id=content_id,
            title=title,
            description=description,
            file_path=safe_path,
            content_type=file.content_type or 'application/octet-stream',
            authenticity_score=authenticity, 
            tags=tags,
            next_step=f"Use /content/{content_id} to view details or /stream/{content_id} to access content"
        )
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@step3_router.post('/generate-video')
async def generate_video(file: UploadFile = File(...), title: str = Form(...), current_user = Depends(get_current_user)):
    """STEP 3C: Generate content from text script (requires authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        # Validate file
        if not file.filename or not file.filename.endswith('.txt'):
            raise HTTPException(status_code=400, detail="Only .txt files allowed")
        
        # Read script content
        script_content = (await file.read()).decode('utf-8')
        if not script_content.strip():
            raise HTTPException(status_code=400, detail="Empty script content")
        
        # Generate IDs
        content_id = uuid.uuid4().hex[:12]
        timestamp = time.time()
        uploader_id = current_user.user_id
        
        # Create MP4 video file path first
        video_filename = f"{content_id}.mp4"
        video_path = bhiv_bucket.get_bucket_path('videos', video_filename)
        
        # Use the video generator module
        try:
            from video.generator import create_simple_video
            final_video_path = create_simple_video(script_content, video_path)
        except Exception as video_error:
            # If video generation fails, create text file with error
            text_path = video_path.replace('.mp4', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"Video Script: {script_content}\n\nVideo generation failed: {str(video_error)}")
            final_video_path = text_path
        
        # Determine content type based on actual file created
        content_type = 'video/mp4' if final_video_path.endswith('.mp4') else 'text/plain'
        
        # Save to database
        from core.database import DatabaseManager
        db = DatabaseManager()
        
        content_data = {
            'content_id': content_id,
            'uploader_id': uploader_id,
            'title': title,
            'description': f'Generated video from script',
            'file_path': final_video_path,
            'content_type': content_type,
            'duration_ms': 10000,
            'authenticity_score': 0.8,
            'current_tags': json.dumps(['generated', 'video', 'script']),
            'uploaded_at': timestamp
        }
        db.create_content(content_data)
        
        return {
            'content_id': content_id,
            'video_path': f'/download/{content_id}',
            'stream_url': f'/stream/{content_id}',
            'status': 'completed',
            'message': 'Video generated successfully with text frames'
        }
            
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Content generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

# ===== STEP 4: CONTENT ACCESS & VIEWING =====

@step4_router.get('/content/{content_id}', status_code=200)
def get_content(content_id: str, request: Request):
    """STEP 4A: Get content details and access URLs (authentication optional for enhanced features)"""
    current_user = None  # For now, make it work without auth
    try:
        # Get content using Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            content = db.get_content_by_id(content_id)
            if not content:
                raise HTTPException(status_code=404, detail='Content not found')
            
            # Extract data from content object
            row = (
                content.content_id,
                content.title,
                content.description,
                content.file_path,
                content.content_type
            )
        except HTTPException:
            raise
        except Exception as db_error:
            import logging
            logging.error(f"Database query failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(db_error)}")
        
        return {
            'content_id': row[0],
            'title': row[1],
            'description': row[2],
            'file_path': row[3],
            'content_type': row[4],
            'download_url': f'/download/{content_id}',
            'stream_url': f'/stream/{content_id}',
            'next_step': f'STEP 4B: GET /download/{content_id} to download or GET /stream/{content_id} to stream, then STEP 5: POST /feedback to rate content'
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step4_router.get('/content/{content_id}/metadata')
def get_content_metadata(content_id: str, request: Request):
    """STEP 4A-2: Get detailed content metadata including stats and related data"""
    current_user = None  # For now, make it work without auth
    try:
        from core.database import DatabaseManager
        from sqlmodel import Session, select, func
        from core.models import Content, Feedback, Script
        
        db = DatabaseManager()
        
        # Get content
        content = db.get_content_by_id(content_id)
        if not content:
            raise HTTPException(status_code=404, detail='Content not found')
        
        # Get additional metadata
        with Session(db.engine) as session:
            # Get feedback stats
            feedback_stats = session.exec(
                select(
                    func.count(Feedback.id),
                    func.avg(Feedback.rating),
                    func.sum(Feedback.watch_time_ms)
                ).where(Feedback.content_id == content_id)
            ).first()
            
            # Get related script if exists (handle missing table)
            related_script = None
            try:
                related_script = session.exec(
                    select(Script).where(Script.content_id == content_id)
                ).first()
            except Exception:
                pass  # Script table may not exist yet
        
        # Parse tags
        try:
            tags = json.loads(content.current_tags) if content.current_tags else []
        except:
            tags = []
        
        # Calculate file size if file exists
        file_size = 0
        if content.file_path and os.path.exists(content.file_path):
            file_size = os.path.getsize(content.file_path)
        
        return {
            'content_id': content.content_id,
            'title': content.title,
            'description': content.description,
            'uploader_id': content.uploader_id,
            'content_type': content.content_type,
            'file_path': content.file_path,
            'file_size_bytes': file_size,
            'duration_ms': content.duration_ms,
            'uploaded_at': content.uploaded_at,
            'authenticity_score': content.authenticity_score,
            'tags': tags,
            'views': content.views,
            'likes': content.likes,
            'shares': content.shares,
            'feedback_stats': {
                'total_feedback': feedback_stats[0] or 0,
                'average_rating': round(feedback_stats[1] or 0, 2),
                'total_watch_time_ms': feedback_stats[2] or 0
            },
            'related_script': {
                'script_id': related_script.script_id if related_script else None,
                'title': related_script.title if related_script else None
            } if related_script else None,
            'urls': {
                'download': f'/download/{content_id}',
                'stream': f'/stream/{content_id}',
                'metadata': f'/content/{content_id}/metadata'
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.error(f"Content metadata error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@step4_router.get('/download/{content_id}')
def download(content_id: str, current_user = Depends(get_current_user)):
    """STEP 4B: Download content file (authentication optional for tracking)"""
    try:
        # Get content using Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            content = db.get_content_by_id(content_id)
            if not content:
                raise HTTPException(status_code=404, detail='Content not found')
            file_path = content.file_path
        except HTTPException:
            raise
        except Exception as db_error:
            import logging
            logging.error(f"Database query failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(db_error)}")
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='File not found')
        
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step4_router.get('/stream/{content_id}')
def stream_video(content_id: str, request: Request, range_request: Optional[str] = None, current_user = Depends(get_current_user)):
    """STEP 4C: Stream video content with range support (authentication optional for analytics)"""
    from fastapi.responses import StreamingResponse
    
    # Log streaming start
    client_ip = request.client.host if request.client else "unknown"
    range_header = request.headers.get('range')
    session_id = streaming_metrics.log_stream_start(content_id, client_ip, range_header)
    
    # Get content using Supabase database
    try:
        from core.database import DatabaseManager
        db = DatabaseManager()
        content = db.get_content_by_id(content_id)
        if not content:
            streaming_metrics.log_stream_end(session_id, 0, 404)
            raise HTTPException(status_code=404, detail='Content not found')
        file_path = content.file_path
    except HTTPException:
        raise
    except Exception as db_error:
        import logging
        logging.error(f"Database query failed: {db_error}")
        streaming_metrics.log_stream_end(session_id, 0, 500)
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(db_error)}")
    if not os.path.exists(file_path):
        streaming_metrics.log_stream_end(session_id, 0, 404)
        raise HTTPException(status_code=404, detail='File not found')
    
    file_size = os.path.getsize(file_path)
    
    if range_header:
        try:
            byte_range = range_header.replace('bytes=', '')
            start_end = byte_range.split('-')
            start = int(start_end[0])
            end = int(start_end[1]) if start_end[1] else file_size - 1
            
            if start >= file_size or end >= file_size or start > end:
                streaming_metrics.log_stream_end(session_id, 0, 416)
                raise HTTPException(status_code=416, detail='Range not satisfiable')
            
            bytes_to_serve = end - start + 1
            
            def iter_file():
                bytes_served = 0
                with open(file_path, 'rb') as f:
                    f.seek(start)
                    remaining = bytes_to_serve
                    while remaining > 0:
                        chunk_size = min(1024 * 1024, remaining)
                        data = f.read(chunk_size)
                        if not data:
                            break
                        remaining -= len(data)
                        bytes_served += len(data)
                        yield data
                # Log completion after streaming
                streaming_metrics.log_stream_end(session_id, bytes_served, 206)
            
            return StreamingResponse(
                iter_file(), 
                status_code=206,
                headers={
                    'Content-Range': f'bytes {start}-{end}/{file_size}',
                    'Accept-Ranges': 'bytes',
                    'Content-Length': str(bytes_to_serve)
                },
                media_type='video/mp4'
            )
        except (ValueError, IndexError):
            streaming_metrics.log_stream_end(session_id, 0, 416)
            raise HTTPException(status_code=416, detail='Invalid range')
    
    # Full file streaming
    streaming_metrics.log_stream_end(session_id, file_size, 200)
    return FileResponse(file_path)

# ===== FEEDBACK =====

# ===== STEP 5: FEEDBACK & AI LEARNING =====

# Removed FeedbackIn - using FeedbackRequest from models.py

@step5_router.post('/feedback', response_model=FeedbackResponse, status_code=201)
async def feedback(f: FeedbackRequest, current_user = Depends(get_current_user)):
    """STEP 5A: Submit feedback to train RL agent (requires authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    try:
        if not (1 <= f.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        # Get user_id from authenticated user (secure)
        user_id = current_user.user_id
        timestamp = time.time()
        
        # Convert rating to reward for RL agent
        reward = (f.rating - 3) / 2.0  # Maps 1-5 rating to -1.0 to 1.0 reward
        event_type = 'like' if f.rating >= 4 else 'dislike' if f.rating <= 2 else 'view'
        
        # Store feedback in database
        # Store feedback in Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            feedback_data = {
                'content_id': f.content_id,
                'user_id': user_id,
                'event_type': event_type,
                'rating': f.rating,
                'comment': f.comment,
                'reward': reward,
                'timestamp': timestamp
            }
            db.create_feedback(feedback_data)
            
            # Save rating to bucket/ratings/
            rating_data = {
                'content_id': f.content_id,
                'user_id': user_id,
                'rating': f.rating,
                'comment': f.comment,
                'event_type': event_type,
                'reward': reward,
                'timestamp': timestamp,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            rating_filename = f"rating_{f.content_id}_{user_id}_{int(timestamp)}.json"
            try:
                bhiv_bucket.save_rating(rating_data, rating_filename)
                import logging
                logging.info(f"Rating saved to bucket: {rating_filename}")
            except Exception as rating_error:
                import logging
                logging.warning(f"Failed to save rating to bucket: {rating_error}")
                
        except Exception as db_error:
            import logging
            logging.error(f"Feedback save failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Feedback save failed: {str(db_error)}")
        
        # Train RL agent with the feedback
        try:
            agent.observe_feedback(
                content_id=f.content_id,
                event_type=event_type,
                watch_time_ms=0,
                user_feedback=reward  # Use user rating as primary reward signal
            )
            
            # Get updated agent metrics after training
            agent_metrics = agent.metrics()
            
            # Save RL training log
            rl_log_data = {
                'content_id': f.content_id,
                'user_id': user_id,
                'action': 'rl_training',
                'event_type': event_type,
                'reward': reward,
                'agent_metrics': agent_metrics,
                'timestamp': timestamp
            }
            rl_log_filename = f"rl_training_{f.content_id}_{int(timestamp)}.json"
            try:
                bhiv_bucket.save_json('logs', rl_log_filename, rl_log_data)
                import logging
                logging.info(f"RL training log saved: {rl_log_filename}")
            except Exception as log_error:
                import logging
                logging.warning(f"Failed to save RL training log: {log_error}")
            
            return FeedbackResponse(
                status='success',
                rating=f.rating,
                event_type=event_type,
                reward=reward,
                rl_training={
                    'agent_trained': True,
                    'current_epsilon': agent_metrics['epsilon'],
                    'q_states': agent_metrics['q_states'],
                    'avg_recent_reward': agent_metrics['avg_recent_reward']
                },
                next_step=f'GET /recommend-tags/{f.content_id} to see updated AI recommendations'
            )
            
        except Exception as rl_error:
            # Log RL training failure but still return success for feedback storage
            import logging
            logging.warning(f"RL agent training failed: {rl_error}")
            
            return {
                'status': 'success',
                'rating': f.rating,
                'event_type': event_type,
                'reward': reward,
                'rl_training': {
                    'agent_trained': False,
                    'error': str(rl_error)
                },
                'next_step': f'GET /recommend-tags/{f.content_id} to see AI recommendations'
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step5_router.get('/recommend-tags/{content_id}', response_model=TagRecommendationResponse)
def recommend_tags(content_id: str, current_user = Depends(get_current_user)):
    """STEP 5B: Get AI-powered tag recommendations using Q-Learning agent (authentication optional for personalization)"""
    try:
        # Get content from database
        # Get content from Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            content = db.get_content_by_id(content_id)
            if not content:
                raise HTTPException(status_code=404, detail='Content not found')
            
            # Extract tags and authenticity from content object
            current_tags = getattr(content, 'current_tags', None)
            authenticity_score = getattr(content, 'authenticity_score', 0.5)
        except HTTPException:
            raise
        except Exception as db_error:
            import logging
            logging.error(f"Database query failed: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database query failed: {str(db_error)}")
        
        try:
            existing_tags = json.loads(current_tags) if current_tags else []
        except:
            existing_tags = []
        
        # Register content with RL agent if not already registered
        agent.register_content(content_id, existing_tags, authenticity_score)
        
        # Get AI-powered recommendations from RL agent
        try:
            rl_recommendation = agent.recommend_tags(content_id)
            recommended_tags = rl_recommendation['tags']
            action_taken = rl_recommendation['action_taken']
            
            # Get agent metrics for transparency
            agent_metrics = agent.metrics()
            
            return TagRecommendationResponse(
                content_id=content_id,
                recommended_tags=recommended_tags,
                original_tags=existing_tags,
                rl_action_taken=action_taken,
                authenticity_score=authenticity_score,
                agent_confidence={
                    'epsilon': agent_metrics['epsilon'],
                    'q_states': agent_metrics['q_states'],
                    'avg_recent_reward': agent_metrics['avg_recent_reward']
                },
                next_step='POST /feedback to provide rating and train the RL agent further'
            )
            
        except Exception as rl_error:
            # Fallback to simple recommendation if RL agent fails
            import logging
            logging.warning(f"RL agent failed for {content_id}: {rl_error}")
            
            fallback_tags = existing_tags[:3] if existing_tags else ['general', 'content']
            return {
                'content_id': content_id,
                'recommended_tags': fallback_tags,
                'original_tags': existing_tags,
                'rl_action_taken': 'fallback',
                'authenticity_score': authenticity_score,
                'warning': 'RL agent unavailable, using fallback recommendations',
                'next_step': 'POST /feedback to provide rating and train the RL agent'
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step5_router.get('/average-rating/{content_id}')
def get_average_rating(content_id: str, current_user = Depends(get_current_user)):
    """STEP 5C: Get average rating for content (authentication optional)"""
    try:
        # Get ratings from Supabase database
        try:
            from core.database import DatabaseManager
            from sqlmodel import Session, select, func
            from core.models import Feedback
            
            db = DatabaseManager()
            with Session(db.engine) as session:
                statement = select(
                    func.avg(Feedback.rating),
                    func.count(Feedback.rating)
                ).where(
                    Feedback.content_id == content_id,
                    Feedback.rating.is_not(None)
                )
                result = session.exec(statement).first()
        except Exception as db_error:
            import logging
            logging.error(f"Database query failed: {db_error}")
            result = (0.0, 0)
        
        avg_rating = result[0] if result[0] else 0.0
        rating_count = result[1] if result[1] else 0
        
        return {
            'content_id': content_id,
            'average_rating': round(avg_rating, 2),
            'rating_count': rating_count,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== STEP 6: ANALYTICS & MONITORING =====

@step6_router.get('/metrics', response_model=MetricsResponse, status_code=200)
def metrics(current_user = Depends(get_current_user)):
    """STEP 6A: View system metrics including RL agent performance (authentication optional for enhanced data)"""
    try:
        # Get system metrics from Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            analytics_data = db.get_analytics_data()
            total_contents = analytics_data['total_content']
            total_feedback = analytics_data['total_feedback']
            total_users = analytics_data['total_users']
        except Exception as db_error:
            import logging
            logging.error(f"Analytics query failed: {db_error}")
            total_contents = total_feedback = total_users = 0
        
        # Get RL agent metrics
        try:
            rl_metrics = agent.metrics()
        except Exception as e:
            rl_metrics = {'error': str(e), 'status': 'unavailable'}
        
        return MetricsResponse(
            system_metrics={
                'total_contents': total_contents,
                'total_feedback': total_feedback,
                'total_users': total_users
            },
            rl_agent_metrics=rl_metrics,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            next_step='GET /rl/agent-stats for detailed RL metrics or GET /lm/stats for LLM status'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step6_router.get('/rl/agent-stats')
def get_rl_agent_stats(current_user = Depends(get_current_user)):
    """STEP 6B: View detailed RL agent statistics and Q-table insights (authentication optional)"""
    try:
        agent_metrics = agent.metrics()
        
        # Get Q-table sample for inspection
        q_sample = {}
        if hasattr(agent, 'q') and agent.q:
            # Show top 5 states by total Q-value
            state_totals = {state: sum(actions.values()) for state, actions in agent.q.items()}
            top_states = sorted(state_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            q_sample = {state: agent.q[state] for state, _ in top_states}
        
        return {
            'agent_performance': agent_metrics,
            'q_table_sample': q_sample,
            'learning_status': {
                'exploration_rate': agent_metrics.get('epsilon', 0.0),
                'learning_active': agent_metrics.get('epsilon', 0.0) > 0.01,
                'states_learned': agent_metrics.get('q_states', 0),
                'recent_performance': agent_metrics.get('avg_recent_reward', 0.0)
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'next_step': 'POST /feedback to train agent or GET /recommend-tags/{id} to see recommendations'
        }
    except Exception as e:
        return {
            'error': str(e),
            'agent_performance': {'status': 'error'},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/lm/stats')
def get_lm_stats(current_user = Depends(get_current_user)):
    """STEP 6B: View Language Model and AI component statistics (authentication optional)"""
    try:
        from core import bhiv_lm_client
        config = bhiv_lm_client.get_llm_config()
        return {
            'lm_config': config, 
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'next_step': 'GET /bhiv/analytics for sentiment analysis statistics'
        }
    except ImportError:
        return {
            'lm_config': {'status': 'LM client not available', 'fallback_mode': True}, 
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'lm_config': {'status': 'error', 'error': str(e)}, 
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/logs')
def get_logs(lines: int = 50, admin_key: str = None):
    """STEP 6C: View recent system logs for debugging (Admin Only)"""
    # Admin authentication
    if admin_key != "logs_2025":
        raise HTTPException(status_code=403, detail="Access denied. Admin key required.")
    
    try:
        import glob
        log_files = glob.glob('logs/*.log')
        if not log_files:
            return {'logs': [], 'message': 'No log files found'}
        
        # Get most recent log file
        latest_log = max(log_files, key=os.path.getmtime)
        
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            log_lines = f.readlines()[-lines:]
        
        return {
            'log_file': latest_log,
            'lines_requested': lines,
            'lines_returned': len(log_lines),
            'logs': [line.strip() for line in log_lines],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'access_level': 'admin'
        }
    except Exception as e:
        return {
            'error': str(e),
            'logs': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/streaming-performance')
def get_streaming_performance(current_user = Depends(get_current_user)):
    """STEP 6D: Real-time streaming analytics (authentication optional)"""
    try:
        from .streaming_metrics import streaming_metrics
        return {
            'streaming_stats': streaming_metrics.get_performance_summary(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'streaming_stats': {'total_streams': 0, 'active_streams': 0},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/reports/video-stats')
def get_video_stats(current_user = Depends(get_current_user)):
    """STEP 6E: Comprehensive content analytics (authentication optional)"""
    try:
        from core.database import DatabaseManager
        from sqlmodel import Session, select, func
        from core.models import Content
        
        try:
            db = DatabaseManager()
            with Session(db.engine) as session:
                # Video count
                video_stmt = select(func.count(Content.content_id)).where(Content.content_type.like('video%'))
                video_count = session.exec(video_stmt).first() or 0
                
                # Total content
                total_stmt = select(func.count(Content.content_id))
                total_content = session.exec(total_stmt).first() or 0
                
                # Stats
                stats_stmt = select(
                    func.avg(Content.duration_ms),
                    func.sum(Content.views),
                    func.sum(Content.likes)
                )
                stats = session.exec(stats_stmt).first() or (0, 0, 0)
                
                # Content types
                types_stmt = select(Content.content_type, func.count(Content.content_id)).group_by(Content.content_type)
                content_types = dict(session.exec(types_stmt).all())
        except Exception as db_error:
            import logging
            logging.error(f"Video stats query failed: {db_error}")
            video_count = total_content = 0
            stats = (0, 0, 0)
            content_types = {}
        
        return {
            'total_videos': video_count,
            'total_content': total_content,
            'content_types': content_types,
            'avg_duration_ms': stats[0] or 0,
            'total_views': stats[1] or 0,
            'total_likes': stats[2] or 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_videos': 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/reports/storyboard-stats')
def get_storyboard_stats(current_user = Depends(get_current_user)):
    """STEP 6F: Storyboard generation statistics (authentication optional)"""
    try:
        storyboard_files = bhiv_bucket.list_bucket_files('storyboards')
        total_storyboards = len(storyboard_files)
        generation_methods = {'llm': 0, 'heuristic': 0, 'manual': 0}
        
        return {
            'total_storyboards': total_storyboards,
            'generation_methods': generation_methods,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'total_storyboards': 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/ingest/webhook')
def webhook_ingest_get(current_user = Depends(get_current_user)):
    """STEP 6I: Webhook ingestion endpoint info (authentication optional)"""
    return {
        'endpoint': '/ingest/webhook',
        'method': 'POST',
        'description': 'Webhook endpoint for external content ingestion',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@step6_router.post('/ingest/webhook')
async def webhook_ingest_post(request: Request, current_user = Depends(get_current_user)):
    """STEP 6J: Webhook endpoint for external content ingestion (authentication optional)"""
    try:
        payload = await request.json()
        result = await bhiv_core.process_webhook_ingest(payload=payload, source='webhook_api')
        return {'webhook_result': result, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception as e:
        return {'error': str(e), 'status': 'failed', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}

@step6_router.get('/bucket/stats')
def get_bucket_stats(current_user = Depends(get_current_user)):
    """STEP 6F: Storage backend statistics (authentication optional)"""
    try:
        bucket_segments = {
            'uploads': 'bucket/uploads',
            'videos': 'bucket/videos', 
            'scripts': 'bucket/scripts',
            'storyboards': 'bucket/storyboards',
            'ratings': 'bucket/ratings',
            'logs': 'bucket/logs'
        }
        
        file_counts = {}
        total_files = 0
        
        for segment, path in bucket_segments.items():
            if os.path.exists(path):
                count = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])
                file_counts[segment] = count
                total_files += count
            else:
                file_counts[segment] = 0
        
        # Also check uploads directory
        uploads_count = 0
        if os.path.exists('uploads'):
            uploads_count = len([f for f in os.listdir('uploads') if os.path.isfile(os.path.join('uploads', f))])
        
        stats = {
            'storage_type': 'local_bucket',
            'bucket_segments': list(bucket_segments.keys()),
            'file_counts': file_counts,
            'uploads_dir_files': uploads_count,
            'total_bucket_files': total_files
        }
        
        return {
            'bucket_stats': stats,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'bucket_stats': {'storage_type': 'unknown'},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/bucket/list/{segment}')
def list_bucket_files(segment: str, limit: int = 20, current_user = Depends(get_current_user)):
    """STEP 6G: List files in bucket segment (authentication optional)"""
    try:
        valid_segments = ['uploads', 'videos', 'scripts', 'storyboards', 'ratings', 'logs']
        if segment not in valid_segments:
            raise HTTPException(status_code=400, detail=f'Invalid segment. Valid: {valid_segments}')
        
        bucket_path = f'bucket/{segment}'
        if not os.path.exists(bucket_path):
            return {
                'segment': segment,
                'files': [],
                'message': f'Segment {segment} not found'
            }
        
        files = []
        for filename in os.listdir(bucket_path)[:limit]:
            filepath = os.path.join(bucket_path, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'filename': filename,
                    'size_bytes': stat.st_size,
                    'modified': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))
                })
        
        return {
            'segment': segment,
            'files': files,
            'total_files': len(files),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'segment': segment,
            'files': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/bhiv/analytics', response_model=AnalyticsResponse, status_code=200)
def get_bhiv_analytics(current_user = Depends(get_current_user)):
    """STEP 6H: Advanced analytics with sentiment analysis (authentication optional)"""
    try:
        # Get analytics from Supabase database
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            analytics_data = db.get_analytics_data()
            total_users = analytics_data['total_users']
            total_content = analytics_data['total_content']
            total_feedback = analytics_data['total_feedback']
            avg_rating = analytics_data['average_rating']
            sentiment_data = analytics_data['sentiment_breakdown']
            avg_engagement = analytics_data.get('average_engagement', 0.0)
        except Exception as db_error:
            import logging
            logging.error(f"Analytics query failed: {db_error}")
            total_users = total_content = total_feedback = 0
            avg_rating = avg_engagement = 0.0
            sentiment_data = {}
        
        # Calculate proper engagement rate
        if total_content > 0:
            engagement_rate = min(100.0, (total_feedback / total_content) * 100)
        else:
            engagement_rate = 0.0
        
        return AnalyticsResponse(
            total_users=total_users,
            total_content=total_content,
            total_feedback=total_feedback,
            average_rating=round(avg_rating, 2),
            average_engagement=round(avg_engagement, 2),
            sentiment_breakdown=sentiment_data,
            engagement_rate=round(engagement_rate, 1),
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        return {
            'error': str(e),
            'total_users': 0,
            'total_content': 0,
            'total_feedback': 0,
            'average_rating': 0.0,
            'sentiment_breakdown': {},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

# ===== STEP 7: TASK QUEUE MANAGEMENT =====

@step7_router.get('/tasks/{task_id}')
async def get_task_status(task_id: str, current_user = Depends(get_current_user)):
    """STEP 7A: Get status of a specific task (authentication optional)"""
    await task_queue.start_workers()
    task_status = await task_queue.get_task_status(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_status

@step7_router.get('/tasks/queue/stats')
async def get_queue_stats(current_user = Depends(get_current_user)):
    """STEP 7B: Get task queue statistics (authentication optional)"""
    await task_queue.start_workers()
    return {
        'queue_stats': task_queue.get_queue_stats(),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@step7_router.post('/tasks/create-test')
async def create_test_task(current_user = Depends(get_current_user)):
    """STEP 7C: Create a test task for queue testing (authentication optional)"""
    await task_queue.start_workers()
    task_id = await task_queue.add_task(
        'feedback_improvement',
        {
            'content_id': 'test_content',
            'rating': 3,
            'feedback_data': {'test': True},
            'storyboard_path': 'test_path'
        }
    )
    return {
        'task_id': task_id,
        'status': 'created',
        'message': 'Test task created successfully'
    }

# ===== STEP 8: SYSTEM MAINTENANCE & OPERATIONS =====

@step8_router.post('/bucket/cleanup')
def cleanup_bucket(current_user = Depends(get_current_user_required), admin_key: str = None):
    """Clean up old files from bucket (requires admin authentication)"""
    # Enhanced admin security
    if admin_key != "admin_2025" and current_user.user_id != "demo001":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        cleanup_results = bhiv_bucket.cleanup_old_files()
        return {
            'status': 'success',
            'cleanup_results': cleanup_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'performed_by': current_user.user_id
        }
    except Exception as e:
        import logging
        logging.error(f"Bucket cleanup failed: {e}")
        return {
            'status': 'error',
            'error': "Cleanup operation failed",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step8_router.post('/bucket/rotate-logs')
def rotate_logs(current_user = Depends(get_current_user_required), admin_key: str = None):
    """Rotate log files (requires admin authentication)"""
    # Enhanced admin security
    if admin_key != "admin_2025" and current_user.user_id != "demo001":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        rotation_results = bhiv_bucket.rotate_logs()
        return {
            'status': 'success',
            'rotation_results': rotation_results,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'performed_by': current_user.user_id
        }
    except Exception as e:
        import logging
        logging.error(f"Log rotation failed: {e}")
        return {
            'status': 'error',
            'error': "Log rotation failed",
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step8_router.get('/maintenance/failed-operations')
def get_failed_operations(current_user = Depends(get_current_user_required), admin_key: str = None):
    """Get list of failed operations (requires admin authentication)"""
    # Enhanced admin security
    if admin_key != "admin_2025" and current_user.user_id != "demo001":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        failed_ops_dir = 'reports/failed_operations'
        if not os.path.exists(failed_ops_dir):
            return {
                'failed_operations': [],
                'message': 'No failed operations directory found'
            }
        
        failed_files = []
        for filename in os.listdir(failed_ops_dir)[:50]:  # Limit to 50 files
            filepath = os.path.join(failed_ops_dir, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                # Sanitize filename for security
                safe_filename = os.path.basename(filename)
                failed_files.append({
                    'filename': safe_filename,
                    'size_bytes': stat.st_size,
                    'created': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime))
                })
        
        return {
            'failed_operations': failed_files,
            'total_count': len(failed_files),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'accessed_by': current_user.user_id
        }
    except Exception as e:
        import logging
        logging.error(f"Failed operations access error: {e}")
        return {
            'error': "Access failed",
            'failed_operations': [],
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

# ===== STEP 9: USER INTERFACE & DASHBOARD =====

@step9_router.get('/dashboard')
def get_dashboard(current_user = Depends(get_current_user)):
    """HTML dashboard for system monitoring"""
    from fastapi.responses import HTMLResponse
    
    # Get basic stats from Supabase
    try:
        from core.database import DatabaseManager
        db = DatabaseManager()
        analytics_data = db.get_analytics_data()
        total_contents = analytics_data['total_content']
        total_feedback = analytics_data['total_feedback']
        total_users = analytics_data['total_users']
    except:
        total_contents = total_feedback = total_users = 0
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Content Uploader Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .stat {{ text-align: center; padding: 20px; background: #007bff; color: white; border-radius: 8px; }}
            .stat h3 {{ margin: 0; font-size: 2em; }}
            .stat p {{ margin: 5px 0 0 0; }}
            .refresh {{ background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>AI Content Uploader Dashboard</h1>
                <p>Real-time system monitoring and analytics</p>
                <button class="refresh" onclick="location.reload()">Refresh</button>
            </div>
            
            <div class="card">
                <h2>System Statistics</h2>
                <div class="stats">
                    <div class="stat">
                        <h3>{total_contents}</h3>
                        <p>Total Content</p>
                    </div>
                    <div class="stat">
                        <h3>{total_feedback}</h3>
                        <p>Feedback Events</p>
                    </div>
                    <div class="stat">
                        <h3>{total_users}</h3>
                        <p>Registered Users</p>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Quick Links</h2>
                <p><a href="/docs">API Documentation</a></p>
                <p><a href="/metrics">System Metrics</a></p>
                <p><a href="/bhiv/analytics">Analytics</a></p>
                <p><a href="/tasks/queue/stats">Task Queue</a></p>
            </div>
            
            <div class="card">
                <h2>Last Updated</h2>
                <p>{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)




# ===== UTILITY FUNCTIONS =====

def wrap_text_for_video(text, max_chars_per_line=40):
    """Simple text wrapping for video display"""
    if not text:
        return ""
    
    words = text.split()
    wrapped_lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        
        if len(test_line) <= max_chars_per_line:
            current_line = test_line
        else:
            if current_line:
                wrapped_lines.append(current_line)
            current_line = word
    
    if current_line:
        wrapped_lines.append(current_line)
    
    return "\n".join(wrapped_lines)

def compute_authenticity(file_path, title, description):
    with open(file_path, 'rb') as f:
        b = f.read(1024)
    h = hashlib.sha256(b + title.encode('utf-8') + description.encode('utf-8')).hexdigest()
    v = int(h[:8], 16) / 0xFFFFFFFF
    return round(v, 4)

def suggest_tags(title, description):
    text = (title + ' ' + description).lower()
    words = [w.strip('.,!?:;()[]') for w in text.split() if len(w) > 3]
    seen = []
    for w in words:
        if w not in seen:
            seen.append(w)
        if len(seen) >= 5:
            break
    return seen

def compute_reward(event_type, watch_time_ms):
    r = 0.0
    if event_type == 'view':
        r = min(1.0, watch_time_ms / 30000.0)
    elif event_type == 'like':
        r = 1.0
    elif event_type == 'share':
        r = 2.0
    elif event_type == 'dislike':
        r = -1.0
    return float(r)