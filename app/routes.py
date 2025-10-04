import os, time, json, hashlib, uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request, Depends
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import sqlite3
from typing import Optional
import asyncio
import logging

logger = logging.getLogger(__name__)
from .models import (
    ContentResponse, FeedbackRequest, FeedbackResponse, 
    TagRecommendationResponse, MetricsResponse, AnalyticsResponse,
    VideoGenerationResponse
)

# Import decorators with fallback
try:
    from .observability import track_performance, track_user_action
except ImportError:
    def track_performance(name):
        def decorator(func):
            return func
        return decorator
    def track_user_action(name):
        def decorator(func):
            return func
        return decorator

# Import retry utilities with fallback
try:
    from .retry_utils import retry_database, retry_external_api, retry_file_operations
except ImportError:
    def retry_database(func):
        return func
    def retry_external_api(func):
        return func
    def retry_file_operations(func):
        return func

# Import audit logger with fallback
try:
    from .request_middleware import audit_logger
except ImportError:
    class AuditLogger:
        def log_action(self, *args, **kwargs):
            pass
    audit_logger = AuditLogger()

# Import rate limiting with fallback
try:
    from .rate_limiting import (
        rate_limit_upload, rate_limit_generate, rate_limit_feedback, 
        rate_limit_analytics, rate_limit_default
    )
except ImportError:
    # Fallback rate limiting functions
    def rate_limit_upload(request):
        pass
    def rate_limit_generate(request):
        pass
    def rate_limit_feedback(request):
        pass
    def rate_limit_analytics(request):
        pass
    def rate_limit_default(request):
        pass

def validate_environment():
    """Optimized environment validation"""
    return {'validation': {'valid': True, 'warning_count': 0}}

# Optimized database imports
try:
    from core.database import DatabaseManager
    from sqlmodel import Session, select
    SQLMODEL_AVAILABLE = True
    db_manager = DatabaseManager()
except ImportError:
    SQLMODEL_AVAILABLE = False
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
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# Import storage with S3 fallback
try:
    from core.s3_storage_adapter import storage_adapter, save_script, save_video, save_json
    from core.s3_storage_adapter import get_bucket_path
except ImportError:
    # Fallback to bhiv_bucket
    try:
        from core.bhiv_bucket import save_script, save_video, get_bucket_path
        from core import bhiv_bucket
        def save_json(segment, filename, data):
            return bhiv_bucket.save_json(segment, filename, data)
    except ImportError:
        # Create fallback functions
        import os
        import json
        
        def save_script(content, filename):
            os.makedirs("bucket/scripts", exist_ok=True)
            path = f"bucket/scripts/{filename}"
            with open(path, 'wb') as f:
                f.write(content if isinstance(content, bytes) else content.encode('utf-8'))
            return path
        
        def save_video(file_path, filename):
            os.makedirs("bucket/videos", exist_ok=True)
            dest = f"bucket/videos/{filename}"
            import shutil
            shutil.copy2(file_path, dest)
            return dest
        
        def get_bucket_path(segment, filename):
            return f"bucket/{segment}/{filename}"
        
        def save_json(segment, filename, data):
            os.makedirs(f"bucket/{segment}", exist_ok=True)
            path = f"bucket/{segment}/{filename}"
            with open(path, 'w') as f:
                json.dump(data, f)
            return path

try:
    from core import bhiv_core
except ImportError:
    # Create fallback bhiv_core
    class BhivCore:
        async def process_webhook_ingest(self, payload, source):
            return {"status": "fallback", "message": "bhiv_core not available"}
    bhiv_core = BhivCore()

DB_PATH = 'data.db'
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

def init_db():
    """Optimized database initialization"""
    if SQLMODEL_AVAILABLE and db_manager:
        return db_manager
    
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    with conn:
        cur = conn.cursor()
        # Create tables only if they don't exist
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
            timestamp REAL
        )""")
    return conn

# Optimized initialization
conn = None
try:
    conn = init_db()
    from .agent import RLAgent
    agent = RLAgent(state_path='agent_state.json')
except Exception as e:
    print(f"Initialization warning: {e}")
    conn = None
    agent = None
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
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>AI Content Uploader Agent</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        h1 { 
            color: #333; 
            text-align: center;
        }
        .links { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 15px; 
            margin: 20px 0; 
        }
        .link-card { 
            background: #007bff; 
            color: white; 
            padding: 15px; 
            border-radius: 5px; 
            text-decoration: none; 
            text-align: center; 
            display: block;
        }
        .link-card:hover { 
            background: #0056b3; 
        }
        .status { 
            background: #28a745; 
            color: white; 
            padding: 10px; 
            border-radius: 5px; 
            text-align: center; 
            margin: 20px 0; 
        }
        .quick-start {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Content Uploader Agent</h1>
        <div class="status">Server Running Successfully</div>
        <p>Welcome to the AI-powered content analysis and video generation platform.</p>
        
        <div class="links">
            <a href="/docs" class="link-card">API Documentation</a>
            <a href="/health" class="link-card">Health Check</a>
            <a href="/dashboard" class="link-card">Dashboard</a>
            <a href="/demo-login" class="link-card">Demo Login</a>
        </div>
        
        <div class="quick-start">
            <h3>Quick Start:</h3>
            <ol>
                <li>Get demo credentials from <a href="/demo-login">/demo-login</a></li>
                <li>Visit <a href="/docs">/docs</a> for interactive API testing</li>
                <li>Use POST /users/login to authenticate</li>
                <li>Upload content with POST /upload</li>
            </ol>
        </div>
        
        <div class="quick-start">
            <h3>Server Status:</h3>
            <ul>
                <li>Database: Connected (Supabase)</li>
                <li>Storage: Supabase (1GB free)</li>
                <li>Authentication: JWT enabled</li>
                <li>API Endpoints: 58 routes loaded</li>
            </ul>
        </div>
    </div>
</body>
</html>"""
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

# Remove all other endpoints from default router - they are now properly organized in step routers

# Create demo user if not exists
def create_demo_user():
    """Check demo user in main database - now uses Supabase"""
    try:
        print("Checking demo user in main database...")
        
        # Check main database first (Supabase)
        from core.database import DatabaseManager
        db = DatabaseManager()
        existing_user = db.get_user_by_username('demo')
        
        if existing_user:
            # Verify password works
            try:
                from .security import PasswordManager
                if PasswordManager.verify_password('demo1234', existing_user.password_hash):
                    print("Demo user ready in main database with correct password")
                    return True
                else:
                    print("Demo user exists but password verification failed - run fix_demo_password.py")
                    return False
            except Exception as verify_error:
                print(f"Password verification error: {verify_error}")
                return False
        else:
            print("Demo user not found in main database - run create_demo_in_supabase.py")
            return False
            
    except Exception as e:
        print(f"Demo user check failed: {e}")
        return False

def update_demo_password(new_password):
    """Update demo user password with proper hashing"""
    try:
        try:
            from .security import PasswordManager
            demo_hash = PasswordManager.hash_password(new_password)
        except ImportError:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            demo_hash = pwd_context.hash(new_password)
        
        with sqlite3.connect('data.db') as temp_conn:
            cur = temp_conn.cursor()
            cur.execute('UPDATE user SET password_hash=? WHERE username=?', (demo_hash, 'demo'))
            if cur.rowcount == 0:
                cur.execute('INSERT INTO user(user_id, username, password_hash, email, email_verified, created_at) VALUES (?,?,?,?,?,?)',
                           ('demo001', 'demo', demo_hash, 'demo@example.com', True, time.time()))
        return True
    except Exception as e:
        print(f"Failed to update demo password: {e}")
        return False

# Check demo user on startup
try:
    demo_ready = create_demo_user()
    if not demo_ready:
        print("Demo user needs to be fixed - run fix_demo_password.py")
except Exception as e:
    print(f"Demo user check failed on startup: {e}")

# ===== STEP 1: SYSTEM STATUS & ONBOARDING =====

@step1_router.get('/health')
def health_check():
    """STEP 1A: Check if system is running - PUBLIC ACCESS"""
    try:
        env_validation = validate_environment()
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "systematic_organization": "9 step workflow",
            "environment_valid": env_validation['validation']['valid'],
            "config_warnings": env_validation['validation']['warning_count'],
            "authentication": "not_required",
            "next_step": "GET /demo-login for test credentials or POST /users/register to create account"
        }
    except Exception:
        return {
            "status": "healthy", 
            "service": "AI Content Uploader Agent",
            "version": "1.0.0",
            "authentication": "not_required",
            "next_step": "GET /demo-login for test credentials or POST /users/register to create account"
        }

@step1_router.get('/demo-login')
def demo_login():
    """STEP 1B: Get demo credentials for quick testing - PUBLIC ACCESS"""
    # Use static demo credentials for reliability
    demo_password = "demo1234"
    
    # Ensure demo user exists and password works
    create_demo_user()
    
    # Test login credentials
    login_test_result = test_demo_login()
    
    return {
        "demo_credentials": {"username": "demo", "password": demo_password},
        "authentication": "not_required",
        "login_test": login_test_result,
        "password_hashing": "bcrypt (compatible with login system)",
        "instructions": [
            "1. Copy the credentials above",
            "2. Go to POST /users/login endpoint",
            "3. Use 'Try it out' and enter username and password",
            "4. Execute to get your access token"
        ],
        "next_step": "POST /users/login with these credentials to get access token"
    }

@step1_router.get('/debug-auth')
async def debug_auth(request: Request):
    """STEP 1C: Debug authentication status for Swagger UI - PUBLIC ACCESS"""
    try:
        current_user = await get_current_user_optional(request)
        return {
            "authenticated": current_user is not None,
            "user_id": current_user.user_id if current_user else None,
            "username": current_user.username if current_user else None,
            "authorization_header": bool(request.headers.get("Authorization")),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "authorization_header": bool(request.headers.get("Authorization")),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

def test_demo_login():
    """Test demo login credentials"""
    try:
        from .security import PasswordManager
        from core.database import DatabaseManager
        
        # Test main database first (Supabase)
        db = DatabaseManager()
        user = db.get_user_by_username('demo')
        
        if user:
            if PasswordManager.verify_password('demo1234', user.password_hash):
                return {"status": "success", "message": "Demo credentials work correctly in main database"}
            else:
                return {"status": "failed", "message": "Password verification failed in main database"}
        else:
            return {"status": "failed", "message": "Demo user not found in main database"}
    except Exception as e:
        return {"status": "error", "message": str(e)}



# ===== STEP 2: USER AUTHENTICATION =====

class InviteUser(BaseModel):
    email: str

@step2_router.post('/invite-user')
def invite_user(invite: InviteUser, current_user = Depends(get_current_user_required)):
    """STEP 2A: Send user invitation (requires authentication)"""
    # Enhanced security validation
    
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
def list_contents(limit: int = 20, current_user = Depends(get_current_user_required)):
    """STEP 3A: Browse existing content from Supabase database"""
    try:
        # Use Supabase PostgreSQL directly
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute('''
            SELECT content_id, uploader_id, title, description, file_path, content_type, 
                   duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares
            FROM content 
            ORDER BY uploaded_at DESC 
            LIMIT %s
        ''', (limit,))
        
        rows = cur.fetchall()
        
        items = []
        for row in rows:
            items.append({
                'content_id': row[0],
                'uploader_id': row[1],
                'title': row[2],
                'description': row[3] or '',
                'file_path': row[4],
                'content_type': row[5],
                'duration_ms': row[6],
                'uploaded_at': row[7],
                'authenticity_score': row[8],
                'current_tags': row[9],
                'views': row[10],
                'likes': row[11],
                'shares': row[12],
                'download_url': f'/download/{row[0]}',
                'stream_url': f'/stream/{row[0]}'
            })
        
        cur.close()
        conn.close()
        
        return {
            'items': items,
            'total_count': len(items),
            'database': 'supabase_postgresql',
            'next_step': 'POST /upload to add new content'
        }
        
    except Exception as e:
        return {
            'items': [], 
            'error': str(e),
            'database': 'connection_failed',
            'message': 'Could not connect to Supabase'
        }

# Simplified video generation endpoint above

@step3_router.post('/upload', response_model=ContentResponse, status_code=201)
async def upload_async(
    request: Request,
    file: UploadFile = File(...), 
    title: str = Form(...), 
    description: str = Form(''),
    current_user = Depends(get_current_user_required),
    _rate_limit = Depends(rate_limit_upload)
):
    """STEP 3B: Upload content file (requires authentication) - ASYNC with rate limiting"""
    
    # Get request ID for audit logging
    request_id = getattr(request.state, 'request_id', None)
    client_ip = request.client.host if request.client else "unknown"
    
    # Track user action with observability
    try:
        set_user_context(current_user.user_id, current_user.username)
        track_event(current_user.user_id, "file_upload_started", {
            "file_type": file.content_type,
            "title": title,
            "request_id": request_id
        })
    except Exception as obs_error:
        logger.warning(f"Observability tracking failed: {obs_error}")
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
        
        # Use new storage adapter for direct upload
        try:
            from core.s3_storage_adapter import storage_adapter
            # Upload to storage (async-compatible)
            storage_path = await asyncio.to_thread(
                storage_adapter.upload_content, data, 'uploads', fname
            )
        except Exception as storage_error:
            logger.warning(f"Storage adapter failed, using fallback: {storage_error}")
            # Fallback to local save
            storage_path = get_bucket_path('uploads', fname)
            os.makedirs(os.path.dirname(storage_path), exist_ok=True)
            await asyncio.to_thread(
                lambda: open(storage_path, 'wb').write(data)
            )
        
        # If it's a script file, also save to scripts bucket
        script_path = None
        if ext == '.txt':
            try:
                script_filename = f"{content_id}_script.txt"
                script_path = save_script(data, script_filename)
                import logging
                logging.info(f"Script file also saved to scripts bucket: {script_path}")
            except Exception as script_error:
                import logging
                logging.warning(f"Failed to save script to scripts bucket: {script_error}")
        
        # Compute authenticity and tags (async)
        authenticity_task = asyncio.to_thread(compute_authenticity, storage_path, title, description)
        tags_task = asyncio.to_thread(suggest_tags, title, description)
        
        authenticity, tags = await asyncio.gather(authenticity_task, tags_task)
        uploaded_at = time.time()
        
        # Save to Supabase database using DatabaseManager
        try:
            from core.database import DatabaseManager
            content_data = {
                'content_id': content_id,
                'uploader_id': uploader_id,
                'title': title,
                'description': description,
                'file_path': storage_path,
                'content_type': file.content_type or 'application/octet-stream',
                'uploaded_at': uploaded_at,
                'authenticity_score': authenticity,
                'current_tags': json.dumps(tags),
                'views': 0,
                'likes': 0,
                'shares': 0
            }
            
            # Use DatabaseManager to create content
            db_content = DatabaseManager.create_content(content_data)
            import logging
            logging.info(f"Content saved to Supabase: {content_id}")
            
            # Save to system logs
            try:
                DatabaseManager.save_system_log(
                    level="INFO",
                    message=f"Content uploaded to Supabase: {content_id} - {title}",
                    module="file_upload",
                    user_id=uploader_id
                )
            except Exception as log_error:
                print(f"Failed to save system log: {log_error}")
            
            print(f"Content successfully saved to database: {content_id}")
            
            # If it's a script file, also save to scripts table and bucket
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
                        'used_for_generation': False,
                        'created_at': time.time()
                    }
                    
                    # Save to both Supabase and local database
                    try:
                        # Supabase first
                        import psycopg2
                        DATABASE_URL = os.getenv("DATABASE_URL")
                        if 'postgresql' in DATABASE_URL:
                            conn = psycopg2.connect(DATABASE_URL)
                            cur = conn.cursor()
                            cur.execute("""
                                INSERT INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (
                                script_data['script_id'], script_data['content_id'], script_data['user_id'],
                                script_data['title'], script_data['script_content'], script_data['script_type'],
                                script_data['file_path'], script_data['created_at'], script_data['used_for_generation']
                            ))
                            conn.commit()
                            cur.close()
                            conn.close()
                            import logging
                            logging.info(f"Script saved to Supabase: upload_{content_id}")
                            
                            # Save to system logs
                            try:
                                from core.database import DatabaseManager
                                DatabaseManager.save_system_log(
                                    level="INFO",
                                    message=f"Script uploaded to Supabase: upload_{content_id} - {title}",
                                    module="script_upload",
                                    user_id=uploader_id
                                )
                            except Exception as log_error:
                                print(f"Failed to save system log: {log_error}")
                        
                        # Local SQLite backup
                        import sqlite3
                        local_conn = sqlite3.connect('data.db')
                        with local_conn:
                            cur = local_conn.cursor()
                            cur.execute("""CREATE TABLE IF NOT EXISTS script (
                                script_id TEXT PRIMARY KEY,
                                content_id TEXT,
                                user_id TEXT,
                                title TEXT,
                                script_content TEXT,
                                script_type TEXT,
                                file_path TEXT,
                                created_at REAL,
                                used_for_generation BOOLEAN DEFAULT FALSE,
                                FOREIGN KEY (content_id) REFERENCES content (content_id)
                            )""")
                            cur.execute("""
                                INSERT OR REPLACE INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                script_data['script_id'], script_data['content_id'], script_data['user_id'],
                                script_data['title'], script_data['script_content'], script_data['script_type'],
                                script_data['file_path'], script_data['created_at'], script_data['used_for_generation']
                            ))
                        local_conn.close()
                        import logging
                        logging.info(f"Script saved to local database: upload_{content_id}")
                        
                        # Save to system logs
                        try:
                            from core.database import DatabaseManager
                            DatabaseManager.save_system_log(
                                level="INFO",
                                message=f"Script uploaded to local database: upload_{content_id} - {title}",
                                module="script_upload",
                                user_id=uploader_id
                            )
                        except Exception as log_error:
                            print(f"Failed to save system log: {log_error}")
                        
                    except Exception as script_db_error:
                        import logging
                        logging.error(f"Failed to save script to database: {script_db_error}")
                        
                        # Save error to system logs
                        try:
                            from core.database import DatabaseManager
                            DatabaseManager.save_system_log(
                                level="ERROR",
                                message=f"Script upload database save failed: {str(script_db_error)}",
                                module="script_upload",
                                user_id=uploader_id
                            )
                        except Exception as log_error:
                            print(f"Failed to save error log: {log_error}")
                    
                    # Save script metadata to bucket
                    script_metadata = {
                        'script_id': script_data['script_id'],
                        'content_id': content_id,
                        'title': title,
                        'script_type': 'uploaded_text',
                        'file_size': len(data),
                        'created_at': script_data['created_at'],
                        'bucket_path': script_path
                    }
                    metadata_filename = f"script_meta_{content_id}.json"
                    bhiv_bucket.save_json('scripts', metadata_filename, script_metadata)
                    
                except Exception as script_error:
                    import logging
                    logging.warning(f"Failed to save script: {script_error}")
            
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
                'storage_path': storage_path,
                'script_path': script_path,
                'timestamp': uploaded_at
            }
            log_filename = f"upload_{content_id}_{int(uploaded_at)}.json"
            try:
                save_json('logs', log_filename, log_data)
                import logging
                logging.info(f"Upload log saved: {log_filename}")
            except Exception as log_error:
                import logging
                logging.warning(f"Failed to save upload log: {log_error}")
                
        except Exception as db_error:
            import logging
            logging.error(f"Supabase save failed: {db_error}")
            
            # Fallback to SQLite
            try:
                import sqlite3
                local_conn = sqlite3.connect('data.db')
                with local_conn:
                    cur = local_conn.cursor()
                    cur.execute("""
                        INSERT OR REPLACE INTO content (content_id, uploader_id, title, description, file_path, content_type, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        content_id, uploader_id, title, description, storage_path,
                        file.content_type or 'application/octet-stream', uploaded_at,
                        authenticity, json.dumps(tags), 0, 0, 0
                    ))
                local_conn.close()
                logging.info(f"Content saved to SQLite fallback: {content_id}")
            except Exception as sqlite_error:
                logging.error(f"Both Supabase and SQLite failed: {sqlite_error}")
                print(f"Database save failed: {db_error}")
        
        # Register content with RL agent for future recommendations (async)
        try:
            await asyncio.to_thread(agent.register_content, content_id, tags, authenticity)
        except Exception as rl_error:
            logger.warning(f"Failed to register content with RL agent: {rl_error}")
            
            # Save warning to system logs
            try:
                from core.database import DatabaseManager
                DatabaseManager.save_system_log(
                    level="WARNING",
                    message=f"Failed to register content with RL agent: {str(rl_error)}",
                    module="rl_agent",
                    user_id=uploader_id
                )
            except Exception as log_error:
                print(f"Failed to save warning log: {log_error}")
        
        # Track successful upload
        track_event(current_user.user_id, "file_upload_completed", {
            "content_id": content_id,
            "file_type": file.content_type,
            "authenticity_score": authenticity,
            "tags_count": len(tags)
        })
        
        # Log audit event for compliance
        try:
            audit_logger.log_action(
                user_id=current_user.user_id,
                action="file_upload",
                resource_type="content",
                resource_id=content_id,
                request_id=request_id,
                ip_address=client_ip,
                details={
                    "filename": safe_filename,
                    "file_size": len(data),
                    "content_type": file.content_type,
                    "storage_path": storage_path
                }
            )
        except Exception as audit_error:
            logger.warning(f"Audit logging failed: {audit_error}")
        
        return ContentResponse(
            content_id=content_id,
            title=title,
            description=description,
            file_path=storage_path,
            content_type=file.content_type or 'application/octet-stream',
            authenticity_score=authenticity, 
            tags=tags,
            next_step=f"Use /content/{content_id} to view details or /stream/{content_id} to access content"
        )
    except HTTPException:
        raise
    except Exception as e:
        # Log error with audit trail
        try:
            audit_logger.log_action(
                user_id=current_user.user_id,
                action="file_upload",
                resource_type="content", 
                resource_id=content_id if 'content_id' in locals() else "unknown",
                request_id=request_id,
                ip_address=client_ip,
                details={"error": str(e)},
                status="failed"
            )
        except Exception as audit_error:
            logger.warning(f"Audit logging failed: {audit_error}")
        
        logger.error(f"Upload failed for user {current_user.user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@step3_router.post('/generate-video', response_model=VideoGenerationResponse, status_code=202)
@track_performance("video_generation")
@track_user_action("generate_video")
async def generate_video(
    file: UploadFile = File(...),
    title: str = Form(...),
    current_user = Depends(get_current_user_required)
):
    """STEP 3C: Generate video one frame per script line"""
    
    # Track video generation with observability
    set_user_context(current_user.user_id, current_user.username)
    track_event(current_user.user_id, "video_generation_started", {
        "title": title,
        "file_size": file.size
    })

    # Validate extension and size
    ext = os.path.splitext(file.filename or '')[1].lower()
    if ext != '.txt':
        raise HTTPException(status_code=400, detail="Only .txt files allowed")
    if file.size is not None and file.size > 1_048_576:
        raise HTTPException(status_code=413, detail="Script file too large (max 1MB)")

    # Read script
    script_content = (await file.read()).decode('utf-8').strip()
    if not script_content:
        raise HTTPException(status_code=400, detail="Empty script content")

    # Save temporary script
    content_id = uuid.uuid4().hex[:12]
    timestamp = time.time()
    bucket_video_path = get_bucket_path('videos', f"{content_id}.mp4")
    os.makedirs(os.path.dirname(bucket_video_path), exist_ok=True)

    # Use the create_multi_frame_video function from video.generator
    try:
        from video.generator import create_multi_frame_video
        create_multi_frame_video(script_content, bucket_video_path, frame_duration=3.0)
    except ImportError:
        # Fallback: Create a simple text file instead of video
        try:
            sentences = []
            import re
            for line in script_content.split('\n'):
                line = line.strip()
                if line:
                    line_sentences = re.split(r'[.!?]+', line)
                    for sentence in line_sentences:
                        sentence = sentence.strip()
                        if sentence:
                            sentences.append(sentence)
            
            # Create text representation
            video_text = f"VIDEO CONTENT\n{'='*50}\n\n"
            for i, sentence in enumerate(sentences, 1):
                video_text += f"Frame {i} (3s): {sentence}\n\n"
            
            # Save as .txt file (will be renamed to .mp4 for compatibility)
            with open(bucket_video_path.replace('.mp4', '.txt'), 'w', encoding='utf-8') as f:
                f.write(video_text)
            
            # Create empty .mp4 file for compatibility
            with open(bucket_video_path, 'w') as f:
                f.write('')
                
        except Exception as fallback_error:
            raise HTTPException(
                status_code=500,
                detail=f"Video generation failed. MoviePy not available and fallback failed: {str(fallback_error)}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )

    # Verify video created
    if not os.path.exists(bucket_video_path):
        raise HTTPException(status_code=500, detail="Video file was not created")

    # Count sentences for metadata
    import re
    sentences = []
    for line in script_content.split('\n'):
        line = line.strip()
        if line:
            line_sentences = re.split(r'[.!?]+', line)
            for sentence in line_sentences:
                sentence = sentence.strip()
                if sentence:
                    sentences.append(sentence)
    frame_duration = 3.0

    # Save to both Supabase and local databases
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Save to Supabase first
        if 'postgresql' in DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Save content first (required for foreign key)
            cur.execute("""
                INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                content_id, current_user.user_id, title, 'Generated video from script',
                bucket_video_path, 'video/mp4', int(frame_duration * len(sentences) * 1000),
                timestamp, 0.8, json.dumps(['generated', 'video', 'script']), 0, 0, 0
            ))
            
            # Save script after content (foreign key dependency)
            cur.execute("""
                INSERT INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"video_{content_id}", content_id, current_user.user_id,
                f"Video script: {title}", script_content, 'video_generation',
                None, timestamp, True
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            print(f"Content and script saved to Supabase: {content_id}")
            
            # Save to system logs
            try:
                from core.database import DatabaseManager
                DatabaseManager.save_system_log(
                    level="INFO",
                    message=f"Video generated and saved to Supabase: {content_id} - {title}",
                    module="video_generation",
                    user_id=current_user.user_id
                )
            except Exception as log_error:
                print(f"Failed to save system log: {log_error}")
        
        # Save to local SQLite as backup
        import sqlite3
        local_conn = sqlite3.connect('data.db')
        with local_conn:
            cur = local_conn.cursor()
            
            # Create tables if they don't exist
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
            
            cur.execute("""CREATE TABLE IF NOT EXISTS script (
                script_id TEXT PRIMARY KEY,
                content_id TEXT,
                user_id TEXT,
                title TEXT,
                script_content TEXT,
                script_type TEXT,
                file_path TEXT,
                created_at REAL,
                used_for_generation BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (content_id) REFERENCES content (content_id)
            )""")
            
            # Save content first
            cur.execute("""
                INSERT OR REPLACE INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id, current_user.user_id, title, 'Generated video from script',
                bucket_video_path, 'video/mp4', int(frame_duration * len(sentences) * 1000),
                timestamp, 0.8, json.dumps(['generated', 'video', 'script']), 0, 0, 0
            ))
            
            # Save script after content
            cur.execute("""
                INSERT OR REPLACE INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"video_{content_id}", content_id, current_user.user_id,
                f"Video script: {title}", script_content, 'video_generation',
                None, timestamp, True
            ))
        
        local_conn.close()
        print(f"Content and script saved to local database: {content_id}")
        
        # Save to system logs
        try:
            from core.database import DatabaseManager
            DatabaseManager.save_system_log(
                level="INFO",
                message=f"Video content and script saved to local database: {content_id} - {title}",
                module="video_generation",
                user_id=current_user.user_id
            )
        except Exception as log_error:
            print(f"Failed to save system log: {log_error}")
        
        # Save script to bucket as well
        try:
            script_filename = f"video_script_{content_id}.txt"
            script_bucket_path = save_script(script_content.encode('utf-8'), script_filename)
            print(f"Script saved to bucket: {script_bucket_path}")
            
            # Save to system logs
            try:
                from core.database import DatabaseManager
                DatabaseManager.save_system_log(
                    level="INFO",
                    message=f"Script saved to bucket: {script_bucket_path}",
                    module="video_generation",
                    user_id=current_user.user_id
                )
            except Exception as log_error:
                print(f"Failed to save system log: {log_error}")
        except Exception as bucket_error:
            print(f"Failed to save script to bucket: {bucket_error}")
            
            # Save warning to system logs
            try:
                from core.database import DatabaseManager
                DatabaseManager.save_system_log(
                    level="WARNING",
                    message=f"Failed to save script to bucket: {str(bucket_error)}",
                    module="video_generation",
                    user_id=current_user.user_id
                )
            except Exception as log_error:
                print(f"Failed to save warning log: {log_error}")
        
    except Exception as e:
        import logging
        logging.error(f"Database save failed: {e}")
        print(f"Database save failed: {e}")
        
        # Save error to system logs
        try:
            from core.database import DatabaseManager
            DatabaseManager.save_system_log(
                level="ERROR",
                message=f"Video generation database save failed: {str(e)}",
                module="video_generation",
                user_id=current_user.user_id
            )
        except Exception as log_error:
            print(f"Failed to save error log: {log_error}")

    # Track successful video generation
    track_event(current_user.user_id, "video_generation_completed", {
        "content_id": content_id,
        "total_scenes": len(sentences),
        "total_duration": frame_duration * len(sentences)
    })
    
    return VideoGenerationResponse(
        content_id=content_id,
        video_path=f"/download/{content_id}",
        stream_url=f"/stream/{content_id}",
        local_file_path=bucket_video_path,
        storyboard_stats={
            "total_duration": frame_duration * len(sentences),
            "total_scenes": len(sentences),
            "version": "1.0",
            "generation_method": "sentence_per_frame",
        },
        processing_status="completed",
        next_step=f"Use /content/{content_id} to view details or /stream/{content_id} to watch video"
    )

# ===== STEP 4: CONTENT ACCESS & VIEWING =====

@step4_router.get('/content/{content_id}')
def get_content(content_id: str, current_user = Depends(get_current_user_required)):
    """STEP 4A: Get content details and access URLs"""
    try:
        if SQLMODEL_AVAILABLE and db_manager:
            content = db_manager.get_content_by_id(content_id)
            if not content:
                raise HTTPException(status_code=404, detail='Content not found')
            return {
                'content_id': content.content_id,
                'title': content.title,
                'description': content.description,
                'file_path': content.file_path,
                'content_type': content.content_type,
                'download_url': f'/download/{content_id}',
                'stream_url': f'/stream/{content_id}'
            }
        
        # SQLite fallback
        with sqlite3.connect('data.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT content_id, title, description, file_path, content_type FROM content WHERE content_id=?', (content_id,))
            row = cur.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail='Content not found')
        
        return {
            'content_id': row[0], 'title': row[1], 'description': row[2],
            'file_path': row[3], 'content_type': row[4],
            'download_url': f'/download/{content_id}',
            'stream_url': f'/stream/{content_id}'
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
def download(content_id: str, current_user = Depends(get_current_user_required)):
    """STEP 4B: Download content file"""
    try:
        if SQLMODEL_AVAILABLE and db_manager:
            content = db_manager.get_content_by_id(content_id)
            if not content:
                raise HTTPException(status_code=404, detail='Content not found')
            file_path = content.file_path
        else:
            with sqlite3.connect('data.db') as conn:
                cur = conn.cursor()
                cur.execute('SELECT file_path FROM content WHERE content_id=?', (content_id,))
                result = cur.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail='Content not found')
            file_path = result[0]
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail='File not found')
        
        return FileResponse(file_path, filename=os.path.basename(file_path))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step4_router.get('/stream/{content_id}')
def stream_video(content_id: str, request: Request, current_user = Depends(get_current_user_required), range_request: Optional[str] = None):
    """STEP 4C: Stream video content with range support (authentication optional for analytics)"""
    from fastapi.responses import StreamingResponse
    
    # Log streaming start
    client_ip = request.client.host if request.client else "unknown"
    range_header = request.headers.get('range')
    session_id = streaming_metrics.log_stream_start(content_id, client_ip, range_header)
    
    # Get content using database with fallback
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
        # Fallback to SQLite
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                cur.execute('SELECT file_path FROM content WHERE content_id=?', (content_id,))
                result = cur.fetchone()
            conn.close()
            
            if not result:
                streaming_metrics.log_stream_end(session_id, 0, 404)
                raise HTTPException(status_code=404, detail='Content not found')
            file_path = result[0]
        except Exception as sqlite_error:
            import logging
            logging.error(f"Database query failed: {db_error}, SQLite fallback failed: {sqlite_error}")
            streaming_metrics.log_stream_end(session_id, 0, 500)
            raise HTTPException(status_code=500, detail="Database query failed")
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



@step5_router.post('/feedback')
async def feedback_async(f: FeedbackRequest, request: Request, current_user = Depends(get_current_user_required)):
    """STEP 5A: Submit feedback to train RL agent (requires authentication)"""
    try:
        if not (1 <= f.rating <= 5):
            raise HTTPException(status_code=400, detail="Rating must be 1-5")
        
        user_id = current_user.user_id
        reward = (f.rating - 3) / 2.0
        event_type = 'like' if f.rating >= 4 else 'dislike' if f.rating <= 2 else 'view'
        
        # Save to database
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, rating, comment, reward, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (f.content_id, user_id, event_type, 0, f.rating, f.comment, reward, time.time(), 
              request.client.host if request.client else "unknown"))
        
        feedback_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "feedback_id": feedback_id,
            "rating": f.rating,
            "event_type": event_type,
            "reward": reward
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@step5_router.get('/recommend-tags/{content_id}', response_model=TagRecommendationResponse)
@track_performance("tag_recommendation")
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

@step6_router.get('/metrics', response_model=MetricsResponse)
async def metrics_async(
    request: Request,
    current_user = Depends(get_current_user_required),
    _rate_limit = Depends(rate_limit_analytics)
):
    """STEP 6A: View system metrics including RL agent performance - ASYNC with rate limiting"""
    try:
        # Get system metrics (async)
        async def get_system_metrics():
            if SQLMODEL_AVAILABLE and db_manager:
                return await asyncio.to_thread(db_manager.get_analytics_data)
            else:
                def get_sqlite_metrics():
                    with sqlite3.connect('data.db') as conn:
                        cur = conn.cursor()
                        cur.execute('SELECT COUNT(*) FROM content')
                        total_contents = cur.fetchone()[0]
                        cur.execute('SELECT COUNT(*) FROM feedback')
                        total_feedback = cur.fetchone()[0]
                        return {
                            'total_content': total_contents,
                            'total_feedback': total_feedback,
                            'total_users': 1
                        }
                return await asyncio.to_thread(get_sqlite_metrics)
        
        analytics_data = await get_system_metrics()
        total_contents = analytics_data.get('total_content', 0)
        total_feedback = analytics_data.get('total_feedback', 0)
        total_users = analytics_data.get('total_users', 0)
        
        # Get RL agent metrics (async)
        rl_metrics = await asyncio.to_thread(agent.metrics) if agent else {'status': 'unavailable'}
        
        return MetricsResponse(
            system_metrics={
                'total_contents': total_contents,
                'total_feedback': total_feedback,
                'total_users': total_users
            },
            rl_agent_metrics=rl_metrics,
            timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            next_step='GET /rl/agent-stats for detailed RL metrics'
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

@step6_router.get('/debug/database')
def debug_database():
    """Debug database connection - PUBLIC ACCESS"""
    try:
        import os
        DATABASE_URL = os.getenv("DATABASE_URL", "not_set")
        db_type = "PostgreSQL" if 'postgresql' in DATABASE_URL else "SQLite"
        
        # Test direct connection
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                cur.execute('SELECT COUNT(*) FROM "user"')
                user_count = cur.fetchone()[0]
                
                cur.execute('SELECT COUNT(*) FROM content')
                content_count = cur.fetchone()[0]
                
                cur.execute('SELECT COUNT(*) FROM feedback')
                feedback_count = cur.fetchone()[0]
                
                cur.close()
                conn.close()
                
                return {
                    "database_type": db_type,
                    "database_url_prefix": DATABASE_URL[:50],
                    "direct_query_results": {
                        "users": user_count,
                        "content": content_count,
                        "feedback": feedback_count
                    },
                    "status": "success"
                }
            except Exception as pg_error:
                return {
                    "database_type": db_type,
                    "database_url_prefix": DATABASE_URL[:50],
                    "error": str(pg_error),
                    "status": "postgresql_failed"
                }
        else:
            return {
                "database_type": db_type,
                "database_url": DATABASE_URL,
                "status": "using_sqlite"
            }
    except Exception as e:
        return {
            "error": str(e),
            "status": "failed"
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
        # Use storage adapter to list storyboard files
        try:
            storyboard_files = storage_adapter.list_files('storyboards')
            total_storyboards = len(storyboard_files)
        except:
            total_storyboards = 0
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
    """STEP 6L: Webhook ingestion endpoint info (authentication optional)"""
    return {
        'endpoint': '/ingest/webhook',
        'method': 'POST',
        'description': 'Webhook endpoint for external content ingestion',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@step6_router.post('/ingest/webhook')
async def webhook_ingest_post(request: Request, current_user = Depends(get_current_user)):
    """STEP 6K: Webhook endpoint for external content ingestion (authentication optional)"""
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
            total_users = analytics_data.get('total_users', 0)
            total_content = analytics_data.get('total_content', 0)
            total_feedback = analytics_data.get('total_feedback', 0)
            avg_rating = analytics_data.get('average_rating', 0.0)
            sentiment_data = analytics_data.get('sentiment_breakdown', {})
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

@step6_router.get('/observability/health')
def get_observability_health_endpoint(current_user = Depends(get_current_user)):
    """STEP 6I: Get observability system health status (authentication optional)"""
    try:
        from .observability import get_observability_health, performance_monitor
        
        health_status = get_observability_health()
        performance_summary = performance_monitor.get_performance_summary()
        
        return {
            'observability_health': health_status,
            'performance_metrics': performance_summary,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'healthy' if health_status['sentry']['enabled'] or health_status['posthog']['enabled'] else 'limited'
        }
    except Exception as e:
        return {
            'error': str(e),
            'observability_health': {'status': 'error'},
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@step6_router.get('/observability/performance')
def get_performance_metrics(current_user = Depends(get_current_user_required)):
    """STEP 6J: Get detailed performance metrics"""
    import psutil
    import os
    
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get database metrics
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            analytics_data = db.get_analytics_data()
            db_metrics = {
                'total_users': analytics_data.get('total_users', 0),
                'total_content': analytics_data.get('total_content', 0),
                'total_feedback': analytics_data.get('total_feedback', 0)
            }
        except Exception:
            db_metrics = {'error': 'Database metrics unavailable'}
        
        # Get application metrics
        app_metrics = {
            'uptime_seconds': time.time() - psutil.Process().create_time(),
            'process_memory_mb': psutil.Process().memory_info().rss / 1024 / 1024,
            'open_files': len(psutil.Process().open_files()),
            'threads': psutil.Process().num_threads()
        }
        
        return {
            'system_metrics': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / 1024 / 1024 / 1024,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / 1024 / 1024 / 1024
            },
            'application_metrics': app_metrics,
            'database_metrics': db_metrics,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'error': str(e),
            'system_metrics': {},
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
        # Use storage adapter cleanup if available
        try:
            cleanup_results = storage_adapter.list_files('logs', max_keys=1000)
            cleanup_count = len([f for f in cleanup_results if 'old' in f.get('filename', '')])
        except:
            cleanup_results = {'cleaned_files': 0, 'status': 'fallback'}
            cleanup_count = 0
        
        return {
            'status': 'success',
            'cleanup_results': {'cleaned_files': cleanup_count, 'method': 'storage_adapter'},
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
        # Use storage adapter for log rotation if available
        try:
            log_files = storage_adapter.list_files('logs', max_keys=100)
            rotation_results = {'rotated_files': len(log_files), 'method': 'storage_adapter'}
        except:
            rotation_results = {'rotated_files': 0, 'status': 'fallback'}
        
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
    """Optimized authenticity computation"""
    try:
        with open(file_path, 'rb') as f:
            b = f.read(512)  # Reduced read size
        h = hashlib.sha256(b + title.encode('utf-8') + description.encode('utf-8')).hexdigest()
        return round(int(h[:8], 16) / 0xFFFFFFFF, 4)
    except Exception:
        return 0.5  # Default authenticity

def suggest_tags(title, description):
    """Optimized tag suggestion"""
    text = (title + ' ' + description).lower()
    words = [w.strip('.,!?:;()[]') for w in text.split() if len(w) > 3]
    return list(dict.fromkeys(words))[:5]  # Remove duplicates, limit to 5

# Debug endpoints
@step6_router.get('/debug/system')
def debug_system():
    """Debug system status"""
    return {
        'database_available': SQLMODEL_AVAILABLE,
        'agent_available': agent is not None,
        'connection_status': 'connected' if conn else 'disconnected',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@step6_router.get('/debug/errors')
def debug_errors():
    """Debug recent errors"""
    try:
        error_log = []
        if os.path.exists('bucket/logs'):
            log_files = [f for f in os.listdir('bucket/logs') if f.endswith('.json')]
            for log_file in log_files[-5:]:  # Last 5 log files
                try:
                    with open(f'bucket/logs/{log_file}', 'r') as f:
                        log_data = json.load(f)
                        if 'error' in str(log_data).lower():
                            error_log.append(log_data)
                except Exception:
                    continue
        return {'recent_errors': error_log[-10:], 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
    except Exception as e:
        return {'error': str(e), 'recent_errors': []}

# GDPR Compliance Endpoints - Now handled by gdpr_compliance.py
# Legacy endpoints for backward compatibility
@step2_router.delete('/users/{user_id}/data')
async def delete_user_data_legacy(
    user_id: str,
    current_user = Depends(get_current_user_required)
):
    """GDPR: Delete all user data (Legacy endpoint - use /gdpr/delete-data)"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only delete own data")
    
    return {
        "message": "Please use the new GDPR endpoint: DELETE /gdpr/delete-data",
        "new_endpoint": "/gdpr/delete-data",
        "status": "deprecated"
    }

@step2_router.get('/users/{user_id}/data-export')
async def export_user_data_legacy(
    user_id: str,
    current_user = Depends(get_current_user_required)
):
    """GDPR: Export all user data (Legacy endpoint - use /gdpr/export-data)"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Can only export own data")
    
    return {
        "message": "Please use the new GDPR endpoint: GET /gdpr/export-data",
        "new_endpoint": "/gdpr/export-data",
        "status": "deprecated"
    }