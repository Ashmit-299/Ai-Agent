# app/main.py
from dotenv import load_dotenv
load_dotenv()  # Must run before any SQLModel import

# Fix psycopg2 import issue for Windows
import sys
try:
    import psycopg2
except ImportError:
    # psycopg2-binary should provide psycopg2 module
    pass

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.templating import Jinja2Templates

# Import Task 6 configuration
from .config import validate_config, get_config, SENTRY_DSN, POSTHOG_API_KEY

# Initialize Sentry and PostHog
try:
    import sentry_sdk
    if SENTRY_DSN:
        sentry_sdk.init(dsn=SENTRY_DSN)
except ImportError:
    sentry_sdk = None

# PostHog initialization
try:
    from posthog import Posthog
    if POSTHOG_API_KEY:
        ph = Posthog(api_key=POSTHOG_API_KEY, host="https://app.posthog.com")
        posthog = ph  # Keep backward compatibility
    else:
        ph = None
        posthog = None
except (ImportError, TypeError):
    ph = None
    posthog = None

# Initialize SQLModel
try:
    from core.db import init_database
    init_database()
except Exception:
    pass  # Will use fallback initialization in startup event
from .routes import router, step1_router, step3_router, step4_router, step5_router, step6_router, step7_router, step8_router, step9_router

# Import other routers with error handling
try:
    from .analytics import router as analytics_router
except ImportError as e:
    print(f"Warning: Analytics router not available: {e}")
    analytics_router = None

try:
    from .analytics_jinja import router as jinja_router
except ImportError as e:
    print(f"Warning: Jinja analytics router not available: {e}")
    jinja_router = None

try:
    from .auth import router as auth_router
except ImportError as e:
    print(f"Warning: Auth router not available: {e}")
    auth_router = None

# Dashboard is now handled by step9_router in routes.py
dashboard_router = None
try:
    from .logging_config import setup_logging, log_security_event
    root_logger, security_logger, rl_logger = setup_logging()
    logger = root_logger
    logger.info("Structured logging initialized")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()
    def log_security_event(event_type, details, client_ip="unknown"):
        logging.warning(f"SECURITY_EVENT: {event_type} | IP: {client_ip} | Details: {details}")
try:
    from .security import rate_limit_middleware, security_manager
except ImportError:
    from fastapi import Request
    class SecurityManager:
        def get_client_ip(self, request):
            return request.client.host if request.client else "unknown"
    security_manager = SecurityManager()
    def rate_limit_middleware(request):
        pass

# Structured logging is configured above

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Create FastAPI app with security configuration
app = FastAPI(
    title='AI Content Uploader Agent',
    description='Secure AI-powered content analysis and recommendation system with Q-Learning RL',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    openapi_tags=[
        {"name": "STEP 1: System Health & Demo Access", "description": "System status and demo credentials"},
        {"name": "STEP 2: User Authentication", "description": "User registration and login"},
        {"name": "STEP 3: Content Upload & Video Generation", "description": "Upload files and generate videos"},
        {"name": "STEP 4: Content Access & Streaming", "description": "Download and stream content"},
        {"name": "STEP 5: AI Feedback & Tag Recommendations", "description": "Submit feedback and get AI recommendations"},
        {"name": "STEP 6: Analytics & Performance Monitoring", "description": "System metrics and analytics"},
        {"name": "STEP 7: Task Queue Management", "description": "Background task processing and queue management"},
        {"name": "STEP 8: System Maintenance & Operations", "description": "System maintenance and cleanup operations"},
        {"name": "STEP 9: User Interface & Dashboard", "description": "Web dashboard and user interface"},
        {"name": "Default Endpoints", "description": "Backwards compatibility endpoints"}
    ]
)

# Enhanced security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost", "testserver", "*.render.com", "*.onrender.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "https://*.render.com", "https://*.onrender.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"]
)

# PostHog middleware
@app.middleware("http")
async def ph_middleware(req: Request, call_next):
    """PostHog analytics middleware"""
    res = await call_next(req)
    if ph and POSTHOG_API_KEY:
        try:
            ph.capture(
                distinct_id="server",
                event="request",
                properties={
                    "path": req.url.path,
                    "status": res.status_code,
                    "method": req.method
                }
            )
        except Exception:
            pass  # Don't fail on tracking errors
    return res

@app.middleware("http")
async def enhanced_security_middleware(request: Request, call_next):
    """Enhanced security, rate limiting, and observability middleware"""
    import time
    start_time = time.time()
    
    try:
        # Enhanced rate limiting
        rate_limit_middleware(request)
        
        # Security headers validation
        client_ip = security_manager.get_client_ip(request)
        safe_method = str(request.method).replace('\n', '').replace('\r', '')
        safe_path = str(request.url.path).replace('\n', '').replace('\r', '')
        safe_ip = str(client_ip).replace('\n', '').replace('\r', '')
        
        # Block suspicious patterns
        suspicious_patterns = ['../', '..\\', '<script', 'javascript:', 'data:', 'vbscript:']
        if any(pattern in safe_path.lower() for pattern in suspicious_patterns):
            log_security_event("SUSPICIOUS_REQUEST", f"Path: {safe_path}", client_ip)
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Log request with sanitized input
        logger.info(f"Request: {safe_method} {safe_path} from {safe_ip}")
        
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Allow framing for docs pages
        if safe_path.startswith('/docs') or safe_path.startswith('/redoc'):
            response.headers["X-Frame-Options"] = "SAMEORIGIN"
        else:
            response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Relaxed CSP for FastAPI docs to work properly
        if safe_path.startswith('/docs') or safe_path.startswith('/redoc') or safe_path == '/openapi.json':
            response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net https://fastapi.tiangolo.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com"
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        
        # Add rate limit headers
        response.headers["X-Rate-Limit-Remaining"] = "100"
        response.headers["X-Rate-Limit-Reset"] = str(int(time.time()) + 3600)
        
        # Performance monitoring
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # PostHog event tracking
        if posthog and POSTHOG_API_KEY:
            try:
                posthog.capture(
                    distinct_id=safe_ip,
                    event="api_request",
                    properties={
                        "path": safe_path,
                        "method": safe_method,
                        "status_code": response.status_code,
                        "process_time": process_time
                    }
                )
            except Exception:
                pass  # Don't fail on tracking errors
        
        return response
        
    except HTTPException as e:
        if e.status_code == 429:
            safe_path = str(request.url.path).replace('\n', '').replace('\r', '')
            log_security_event("RATE_LIMIT_EXCEEDED", f"Path: {safe_path}", client_ip)
        elif e.status_code == 400:
            log_security_event("INVALID_REQUEST", f"Path: {safe_path}", client_ip)
        raise e
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        # Capture exception in Sentry
        if sentry_sdk and SENTRY_DSN:
            sentry_sdk.capture_exception(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# Include routes in proper systematic sequential order
app.include_router(router)         # Backwards compatibility (included first)
app.include_router(step1_router)   # STEP 1: System Health & Demo Access
if auth_router:                    # STEP 2: User Authentication
    app.include_router(auth_router)
app.include_router(step3_router)   # STEP 3: Content Upload & Video Generation
app.include_router(step4_router)   # STEP 4: Content Access & Streaming
app.include_router(step5_router)   # STEP 5: AI Feedback & Tag Recommendations
app.include_router(step6_router)   # STEP 6: Analytics & Performance Monitoring
app.include_router(step7_router)   # STEP 7: Task Queue Management
app.include_router(step8_router)   # STEP 8: System Maintenance & Operations
app.include_router(step9_router)   # STEP 9: User Interface & Dashboard
if jinja_router:                   # Jinja2 Dashboard (Optional)
    app.include_router(jinja_router)
# Analytics endpoints are now included in step6_router above
# Dashboard is included in step9_router above

# Fallback handling is now integrated into main routes

# Mount static files for generated videos
try:
    app.mount("/generated", StaticFiles(directory="/tmp"), name="generated")
except Exception:
    pass  # Skip if directory doesn't exist

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("AI Content Uploader Agent starting up...")
    logger.info("Security features: Rate limiting, Input validation, File type restrictions")
    
    # Validate Task 6 configuration
    config_valid = validate_config()
    if config_valid:
        logger.info("Task 6 configuration validated successfully")
    else:
        logger.warning("Task 6 configuration incomplete - some features may be limited")
    
    # Initialize Sentry and PostHog
    if sentry_sdk and SENTRY_DSN:
        sentry_sdk.capture_message("Application startup")
        logger.info("Sentry monitoring initialized")
    
    if posthog and POSTHOG_API_KEY:
        posthog.capture(distinct_id="system", event="startup")
        logger.info("PostHog analytics initialized")
    
    # Initialize database
    try:
        # Try SQLModel first
        from core.db import init_database
        if init_database():
            logger.info("SQLModel database initialized successfully")
        else:
            logger.info("Using SQLite fallback database")
    except Exception as e:
        logger.warning(f"Database initialization failed: {e}")
        # Routes will handle fallback automatically

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("AI Content Uploader Agent shutting down...")

# Sentry exception handler
@app.exception_handler(Exception)
async def capture_exc(req: Request, exc: Exception):
    """Capture exceptions in Sentry"""
    if sentry_sdk and SENTRY_DSN:
        sentry_sdk.capture_exception(exc)
    logger.error(f"Unhandled exception: {exc}")
    raise exc

# Health check endpoint is now properly organized in STEP 1 router
