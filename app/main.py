# app/main.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
warnings.filterwarnings("ignore", category=UserWarning, module="sqlmodel")
warnings.filterwarnings("ignore", category=UserWarning, module="passlib")
print("Bcrypt warnings suppressed")

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

# Add new middleware imports
try:
    from .request_middleware import RequestIDMiddleware, StructuredLoggingMiddleware, audit_logger
except ImportError:
    # Fallback middleware classes
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class RequestIDMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class StructuredLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class AuditLogger:
        def log_action(self, *args, **kwargs):
            pass
    
    audit_logger = AuditLogger()

# Import global authentication middleware
try:
    from .auth_middleware import GlobalAuthMiddleware
except ImportError:
    from starlette.middleware.base import BaseHTTPMiddleware
    class GlobalAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)

try:
    from .jwks_auth import (
        get_current_user_supabase as get_current_user_required_supabase,
        get_current_user_supabase_optional as get_current_user_optional_supabase,
        supabase_auth_dependency as require_auth
    )
except ImportError:
    # Fallback functions
    async def get_current_user_required_supabase(request):
        return None
    async def get_current_user_optional_supabase(request):
        return None
    async def require_auth(request):
        return None

try:
    from .retry_utils import retry_llm_service, retry_database, retry_external_api
except ImportError:
    # Fallback decorators
    def retry_llm_service(func):
        return func
    def retry_database(func):
        return func
    def retry_external_api(func):
        return func
try:
    from .middleware import (
        AuthenticationMiddleware,
        ObservabilityMiddleware, 
        UserContextMiddleware, 
        ErrorHandlingMiddleware,
        RequestLoggingMiddleware,
        InputValidationMiddleware,
        get_system_health
    )
except ImportError:
    # Fallback middleware classes
    from starlette.middleware.base import BaseHTTPMiddleware
    
    class AuthenticationMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class ObservabilityMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class UserContextMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class ErrorHandlingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class RequestLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    class InputValidationMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            return await call_next(request)
    
    async def get_system_health():
        return {"status": "healthy", "middleware": "fallback"}
from .observability import performance_monitor

# Prometheus metrics integration
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Prometheus instrumentator not available - install with: pip install prometheus-fastapi-instrumentator")

# Initialize SQLModel - use existing database module
try:
    from core.database import create_db_and_tables
    create_db_and_tables()
except Exception as e:
    print(f"Database initialization warning: {e}")
    pass  # Will use fallback initialization in startup event
from .routes import router, step1_router, step3_router, step4_router, step5_router, step6_router, step7_router, step8_router, step9_router
from .cdn_fixed import router as cdn_router
from .simple_feedback_route import router as simple_feedback_router

# Import presigned URLs router with fallback
try:
    from .presigned_urls import router as presigned_router
except ImportError:
    presigned_router = None

# Import GDPR compliance router with fallback
try:
    from .gdpr_compliance import router as gdpr_router
except ImportError:
    gdpr_router = None

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
        async def authenticate_request(self, request):
            return None
    security_manager = SecurityManager()
    def rate_limit_middleware(request):
        pass

# Structured logging is configured above

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Create FastAPI app with JWT authentication support
app = FastAPI(
    title='AI Content Uploader Agent',
    description='AI-powered content analysis and recommendation system',
    version='1.0.0'
)

# Add JWT security scheme
from fastapi.security import HTTPBearer
security = HTTPBearer()

# Add security to app
app.add_security_scheme = security



# Simplified OpenAPI configuration to avoid schema resolution errors
def get_openapi_schema():
    if app.openapi_schema:
        return app.openapi_schema
    
    from fastapi.openapi.utils import get_openapi
    
    try:
        # Generate basic schema
        openapi_schema = get_openapi(
            title="AI Content Uploader Agent",
            version="1.0.0",
            description="AI-powered content analysis system with JWT authentication",
            routes=app.routes,
        )
        
        # Add security configuration
        if "components" not in openapi_schema:
            openapi_schema["components"] = {}
        
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
        
        # Add missing validation error schemas
        if "schemas" not in openapi_schema["components"]:
            openapi_schema["components"]["schemas"] = {}
        
        # Add HTTPValidationError schema
        openapi_schema["components"]["schemas"]["HTTPValidationError"] = {
            "title": "HTTPValidationError",
            "type": "object",
            "properties": {
                "detail": {
                    "title": "Detail",
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ValidationError"}
                }
            }
        }
        
        # Add ValidationError schema
        openapi_schema["components"]["schemas"]["ValidationError"] = {
            "title": "ValidationError",
            "required": ["loc", "msg", "type"],
            "type": "object",
            "properties": {
                "loc": {
                    "title": "Location",
                    "type": "array",
                    "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]}
                },
                "msg": {"title": "Message", "type": "string"},
                "type": {"title": "Error Type", "type": "string"}
            }
        }
        
        # Add global authentication to all endpoints except public ones
        public_paths = [
            "/health", "/docs", "/openapi.json", "/redoc", "/docs/oauth2-redirect",
            "/users/login", "/users/register", "/demo-login"  # Keep auth endpoints public
        ]
        
        if "paths" in openapi_schema:
            for path, methods in openapi_schema["paths"].items():
                if path not in public_paths:
                    for method, details in methods.items():
                        if method.lower() != "options":
                            if "security" not in details:
                                details["security"] = [{"BearerAuth": []}]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
        
    except Exception as e:
        # Fallback to minimal schema if generation fails
        print(f"OpenAPI schema generation error: {e}")
        minimal_schema = {
            "openapi": "3.0.2",
            "info": {
                "title": "AI Content Uploader Agent",
                "version": "1.0.0"
            },
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            },
            "paths": {}
        }
        app.openapi_schema = minimal_schema
        return app.openapi_schema

app.openapi = get_openapi_schema

# Custom docs endpoint with inline CSS/JS to avoid CDN issues
@app.get("/docs", include_in_schema=False)
async def custom_docs():
    from fastapi.responses import HTMLResponse
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>AI Content Uploader Agent - API Docs</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-standalone-preset.js"></script>
    <script>
    window.onload = function() {
      SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
      });
    };
    </script>
</body>
</html>
    """)

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
async def debug_auth_main(request: Request):
    """Debug endpoint to check authentication status - Tests both Supabase and local auth"""
    try:
        # Check for authorization header directly
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            
            # Try Supabase authentication first
            try:
                from .jwks_auth import get_current_user_supabase_optional
                supabase_user = await get_current_user_supabase_optional(request)
                if supabase_user:
                    return {
                        "authenticated": True,
                        "auth_type": "supabase",
                        "user_id": supabase_user.user_id,
                        "username": supabase_user.username,
                        "email": supabase_user.email,
                        "role": supabase_user.role,
                        "token_type": supabase_user.token_type,
                        "message": "✅ Supabase JWKS Authentication working!",
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
            except Exception as supabase_error:
                pass  # Try local auth
            
            # Try local authentication
            try:
                user_data = await security_manager.authenticate_request(request)
                if user_data:
                    return {
                        "authenticated": True,
                        "auth_type": "local",
                        "user_id": user_data.get("user_id"),
                        "username": user_data.get("username"),
                        "token_type": user_data.get("token_type", "local"),
                        "message": "✅ Local JWT Authentication working!",
                        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
            except Exception as local_error:
                return {
                    "authenticated": False,
                    "message": f"❌ Both auth methods failed - Supabase and Local",
                    "local_error": str(local_error),
                    "help": "Get a new token from /users/login or use valid Supabase token",
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }
        
        return {
            "authenticated": False,
            "message": "❌ No authorization header found",
            "auth_header_present": bool(auth_header),
            "help": "Click the green 'Authorize' button in Swagger UI and enter a Bearer token",
            "instructions": [
                "1. For local auth: Get token from POST /users/login (username: demo, password: demo1234)",
                "2. For Supabase auth: Use valid Supabase JWT token",
                "3. Click 🔒 Authorize button at top of page",
                "4. Enter token in format: your_token_here (no 'Bearer ' prefix)",
                "5. Click Authorize, then test this endpoint again"
            ],
            "supported_auth_types": ["local_jwt", "supabase_jwks", "supabase_secret"],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
            
    except Exception as e:
        return {
            "authenticated": False,
            "error": str(e),
            "message": "Authentication check failed",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

@app.get("/debug-routes", tags=["Debug"])
async def debug_routes():
    """Debug endpoint to list all available routes"""
    try:
        routes_info = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes_info.append({
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                    "name": getattr(route, 'name', 'unnamed')
                })
        
        # Filter upload-related routes
        upload_routes = [r for r in routes_info if 'upload' in r['path'].lower()]
        
        return {
            "total_routes": len(routes_info),
            "upload_routes": upload_routes,
            "all_routes": routes_info[:20],  # First 20 routes
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to enumerate routes",
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

# Add input validation middleware FIRST for security
try:
    from .input_validation import InputValidationMiddleware
    app.add_middleware(
        InputValidationMiddleware,
        max_body_size=100 * 1024 * 1024  # 100MB request body limit
    )
    logger.info("Enhanced input validation middleware enabled")
except ImportError as e:
    logger.warning(f"Input validation middleware not available: {e}")

# Add global authentication middleware (SECOND - after validation)
app.add_middleware(GlobalAuthMiddleware)

# Add new middleware for endpoint hardening
app.add_middleware(RequestIDMiddleware)
app.add_middleware(StructuredLoggingMiddleware)

print(f"DEBUG: Middleware added successfully")
print(f"DEBUG: Server will be available on port 9000")

# Add rate limiting middleware
try:
    from .rate_limit_middleware import RateLimitMiddleware
    app.add_middleware(RateLimitMiddleware)
except ImportError:
    pass  # Rate limiting middleware not available

# Simplified CORS middleware for reliable operation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add observability and authentication endpoints
@app.get("/health/detailed")
async def health_detailed():
    """Detailed health check with observability and auth status"""
    try:
        health_data = await get_system_health()
        
        # Add Supabase auth health
        try:
            from .jwks_auth import get_supabase_auth_health
            health_data["supabase_auth"] = get_supabase_auth_health()
        except Exception as e:
            health_data["supabase_auth"] = {"error": str(e), "available": False}
        
        return health_data
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }

@app.get("/metrics/performance")
async def performance_metrics():
    """Get performance metrics summary"""
    import psutil
    
    try:
        # Get basic system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Get process metrics
        process = psutil.Process()
        
        return {
            'metrics': {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_available_mb': memory.available / 1024 / 1024,
                'process_memory_mb': process.memory_info().rss / 1024 / 1024,
                'uptime_seconds': time.time() - process.create_time(),
                'threads_count': process.num_threads()
            },
            'slow_operations_count': 0,
            'recent_slow_operations': [],
            'prometheus_available': PROMETHEUS_AVAILABLE,
            'prometheus_endpoint': '/metrics/prometheus' if PROMETHEUS_AVAILABLE else None,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {
            'metrics': {'error': str(e)},
            'slow_operations_count': 0,
            'recent_slow_operations': [],
            'prometheus_available': PROMETHEUS_AVAILABLE,
            'prometheus_endpoint': '/metrics/prometheus' if PROMETHEUS_AVAILABLE else None,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }

@app.get("/metrics")
async def metrics_info():
    """Get available metrics endpoints"""
    return {
        "available_endpoints": {
            "performance": "/metrics/performance",
            "prometheus": "/metrics/prometheus" if PROMETHEUS_AVAILABLE else None,
            "observability": "/observability/health"
        },
        "prometheus_enabled": PROMETHEUS_AVAILABLE,
        "description": "AI Agent metrics collection endpoints",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.get("/monitoring-status")
async def monitoring_status():
    """Get monitoring system status"""
    try:
        sentry_configured = bool(os.getenv("SENTRY_DSN"))
        posthog_configured = bool(os.getenv("POSTHOG_API_KEY"))
        monitoring_healthy = sentry_configured or posthog_configured
        
        return {
            "status": "healthy" if monitoring_healthy else "limited",
            "monitoring_systems": {
                "sentry": {"configured": sentry_configured},
                "posthog": {"configured": posthog_configured},
                "prometheus": {"available": PROMETHEUS_AVAILABLE}
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')}

@app.middleware("http")
async def simple_middleware(request: Request, call_next):
    """Simple middleware for performance tracking"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routes in proper systematic sequential order
# Note: Order matters to avoid route conflicts
app.include_router(router)         # Backwards compatibility (included first)
app.include_router(step1_router)   # STEP 1: System Health & Demo Access
if auth_router:                    # STEP 2: User Authentication
    app.include_router(auth_router)
app.include_router(step3_router)   # STEP 3: Content Upload & Video Generation
app.include_router(step4_router)   # STEP 4: Content Access & Streaming
app.include_router(step5_router)   # STEP 5: AI Feedback & Tag Recommendations
app.include_router(simple_feedback_router)  # Simple feedback endpoint that works
app.include_router(step6_router)   # STEP 6: Analytics & Performance Monitoring
app.include_router(step7_router)   # STEP 7: Task Queue Management
app.include_router(step8_router)   # STEP 8: System Maintenance & Operations
app.include_router(step9_router)   # STEP 9: User Interface & Dashboard
app.include_router(cdn_router)     # CDN & Pre-signed URLs (with /cdn prefix)
if presigned_router:               # Pre-signed URLs for S3/MinIO
    app.include_router(presigned_router)
    print(f"DEBUG: Presigned router included with {len([r for r in presigned_router.routes])} routes")
else:
    print("DEBUG: Presigned router not available - check import errors")
if gdpr_router:                    # GDPR Compliance & Privacy
    app.include_router(gdpr_router)
if jinja_router:                   # Jinja2 Dashboard (Optional)
    app.include_router(jinja_router)

print(f"DEBUG: Loaded {len(app.routes)} total routes")
print(f"DEBUG: CDN router included with prefix /cdn")
print(f"DEBUG: Main upload route: POST /upload")
print(f"DEBUG: CDN upload route: POST /cdn/upload/{{token}}")
# Analytics endpoints are now included in step6_router above
# Dashboard is included in step9_router above

# Debug route information
try:
    route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
    upload_routes = [path for path in route_paths if 'upload' in path.lower()]
    print(f"DEBUG: Upload-related routes found: {upload_routes}")
except Exception as e:
    print(f"DEBUG: Could not enumerate routes: {e}")

# Fallback handling is now integrated into main routes

# Mount static files for generated videos
try:
    import tempfile
    temp_dir = tempfile.gettempdir()
    app.mount("/generated", StaticFiles(directory=temp_dir), name="generated")
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
    
    # Initialize Prometheus metrics
    if PROMETHEUS_AVAILABLE:
        try:
            instrumentator = Instrumentator(
                should_group_status_codes=False,
                should_ignore_untemplated=True,
                should_respect_env_var=True,
                should_instrument_requests_inprogress=True,
                excluded_handlers=["/health", "/metrics"],
                env_var_name="ENABLE_METRICS",
                inprogress_name="fastapi_inprogress",
                inprogress_labels=True
            )
            instrumentator.instrument(app).expose(app, include_in_schema=False, endpoint="/metrics/prometheus")
            logger.info("Prometheus metrics enabled at /metrics/prometheus")
        except Exception as e:
            logger.warning(f"Prometheus metrics initialization failed: {e}")
    else:
        logger.info("Prometheus metrics not available")
    
    # Validate Task 6 configuration
    config_valid = validate_config()
    if config_valid:
        logger.info("Task 6 configuration validated successfully")
    else:
        logger.warning("Task 6 configuration incomplete - some features may be limited")
    
    # Initialize database
    try:
        # Try SQLModel first
        from core.database import create_db_and_tables
        create_db_and_tables()
        logger.info("Database initialized successfully")
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
