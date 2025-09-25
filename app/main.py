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
import time
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer

# Import Task 6 configuration
from .config import validate_config, get_config, SENTRY_DSN, POSTHOG_API_KEY

# Initialize advanced observability system
from .observability import sentry_manager, posthog_manager, structured_logger
from .middleware import (
    ObservabilityMiddleware, 
    UserContextMiddleware, 
    ErrorHandlingMiddleware,
    get_system_health
)
from .observability import performance_monitor

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

# Configure OpenAPI security scheme for Swagger UI
security = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    if "components" not in openapi_schema:
        openapi_schema["components"] = {}
    
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Set global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Set security for specific endpoints - debug-auth should require auth to test properly
    if "paths" in openapi_schema:
        public_endpoints = [
            "/",
            "/test",
            "/health",
            "/demo-login", 
            "/users/register",
            "/users/login"
        ]
        
        # Make debug-auth require authentication to test the authorize button
        auth_test_endpoints = ["/debug-auth"]
        
        for endpoint_path in public_endpoints:
            if endpoint_path in openapi_schema["paths"]:
                for method_name, method_info in openapi_schema["paths"][endpoint_path].items():
                    if isinstance(method_info, dict):
                        # Set empty security array to override global security
                        method_info["security"] = []
        
        # Ensure debug-auth requires authentication
        for endpoint_path in auth_test_endpoints:
            if endpoint_path in openapi_schema["paths"]:
                for method_name, method_info in openapi_schema["paths"][endpoint_path].items():
                    if isinstance(method_info, dict):
                        # Require BearerAuth for testing
                        method_info["security"] = [{"BearerAuth": []}]
    

    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Test endpoint for data saving
@app.post("/test-data-saving", tags=["Testing"])
async def test_data_saving(request: Request):
    """Test endpoint to verify data is saving to both bucket and database - REQUIRES AUTHENTICATION"""
    try:
        from app.auth import get_current_user_required
        current_user = await get_current_user_required(request)
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication required")

    
    try:
        import time
        from core import bhiv_bucket
        from core.database import DatabaseManager
        
        timestamp = time.time()
        test_id = f"test_{int(timestamp)}_{current_user.user_id}"
        
        # Test bucket saving
        bucket_data = {
            'test_id': test_id,
            'message': 'Test bucket saving',
            'timestamp': timestamp,
            'type': 'bucket_test'
        }
        
        bucket_results = {}
        for segment in ['scripts', 'logs', 'storyboards', 'ratings']:
            try:
                filename = f"{segment}_test_{test_id}.json"
                bhiv_bucket.save_json(segment, filename, bucket_data)
                bucket_results[segment] = 'success'
            except Exception as e:
                bucket_results[segment] = f'failed: {str(e)}'
        
        # Test database saving
        db_results = {}
        try:
            db = DatabaseManager()
            
            # Test system log
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                with conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO system_logs (level, message, module, timestamp, user_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', ('INFO', f'Test log {test_id}', 'test', timestamp, 'test_user'))
                db_results['system_logs'] = 'success'
                conn.close()
            except Exception as e:
                db_results['system_logs'] = f'failed: {str(e)}'
            
            # Test analytics
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                with conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO analytics (event_type, user_id, content_id, event_data, timestamp, ip_address)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', ('test_event', 'test_user', None, f'{{"test_id": "{test_id}"}}', timestamp, '127.0.0.1'))
                db_results['analytics'] = 'success'
                conn.close()
            except Exception as e:
                db_results['analytics'] = f'failed: {str(e)}'
                
        except Exception as e:
            db_results['database'] = f'failed: {str(e)}'
        
        return {
            'test_id': test_id,
            'user_id': current_user.user_id,
            'username': current_user.username,
            'timestamp': timestamp,
            'bucket_results': bucket_results,
            'database_results': db_results,
            'message': 'Data saving test completed'
        }
        
    except Exception as e:
        return {
            'error': str(e), 
            'message': 'Data saving test failed',
            'user_id': current_user.user_id if current_user else 'unknown'
        }

# Debug endpoint for authentication testing
@app.get("/debug-auth", tags=["Authentication Test"])
async def debug_auth(request: Request):
    """Debug endpoint to check authentication status - Tests Swagger UI Authorization"""
    try:
        # Check for authorization header directly
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            # Try to authenticate using security manager
            try:
                user_data = await security_manager.authenticate_request(request)
                if user_data:
                    return {
                        "authenticated": True,
                        "user_id": user_data.get("user_id"),
                        "username": user_data.get("username"),
                        "message": "✅ Swagger UI Authorization working!",
                        "auth_header_present": True,
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
            except Exception as auth_error:
                return {
                    "authenticated": False,
                    "message": f"❌ Token invalid: {str(auth_error)}",
                    "auth_header_present": True,
                    "help": "Get a new token from /users/login",
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
        
        return {
            "authenticated": False,
            "message": "❌ No authorization header found",
            "auth_header_present": bool(auth_header),
            "help": "Click the green 'Authorize' button in Swagger UI and enter a Bearer token",
            "instructions": [
                "1. Get token from POST /users/login (username: demo, password: demo1234)",
                "2. Click 🔒 Authorize button at top of page",
                "3. Enter token in format: your_token_here (no 'Bearer ' prefix)",
                "4. Click Authorize, then test this endpoint again"
            ],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
            
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "message": "Authentication check failed",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

# Add middleware in correct order (last added runs first)
app.add_middleware(ObservabilityMiddleware)
app.add_middleware(UserContextMiddleware)  
app.add_middleware(ErrorHandlingMiddleware)

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

# Add observability endpoints
@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check with observability status"""
    return await get_system_health()

@app.get("/metrics/performance")
async def performance_metrics():
    """Get performance metrics summary"""
    return performance_monitor.get_performance_summary()

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
        
        # Advanced event tracking
        try:
            # Log security events if suspicious
            if response.status_code >= 400:
                structured_logger.log_security_event(
                    "HTTP_ERROR",
                    client_ip=safe_ip,
                    details={
                        "path": safe_path,
                        "method": safe_method,
                        "status_code": response.status_code
                    }
                )
        except Exception:
            pass
        
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
        # Capture exception with advanced observability
        try:
            sentry_manager.capture_exception(e, {
                "path": safe_path,
                "method": safe_method,
                "client_ip": client_ip
            })
        except Exception:
            pass
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
    structured_logger.log_business_event("application_startup", metadata={
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": os.getenv("GIT_SHA", "unknown")
    })
    
    logger.info("AI Content Uploader Agent starting up...")
    logger.info("Security features: Rate limiting, Input validation, File type restrictions")
    
    # Validate Task 6 configuration
    config_valid = validate_config()
    if config_valid:
        logger.info("Task 6 configuration validated successfully")
    else:
        logger.warning("Task 6 configuration incomplete - some features may be limited")
    
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
    structured_logger.log_business_event("application_shutdown")
    logger.info("AI Content Uploader Agent shutting down...")

# Advanced exception handler
@app.exception_handler(Exception)
async def capture_exc(req: Request, exc: Exception):
    """Capture exceptions with advanced observability"""
    sentry_manager.capture_exception(exc, {
        "path": req.url.path,
        "method": req.method,
        "client_ip": req.client.host if req.client else "unknown"
    })
    
    logger.error(f"Unhandled exception: {exc}")
    raise exc

# Health check endpoint is now properly organized in STEP 1 router
