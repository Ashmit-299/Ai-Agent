#!/usr/bin/env python3
"""
FastAPI middleware for observability and monitoring
"""

import time
import json
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    from .observability import (
        sentry_manager, posthog_manager, performance_monitor, 
        structured_logger, track_event, set_user_context
    )
except ImportError:
    # Fallback implementations
    class MockManager:
        def capture_exception(self, *args, **kwargs): pass
        def track_event(self, *args, **kwargs): pass
        def get_performance_summary(self): return {}
        def log_api_request(self, *args, **kwargs): pass
    
    sentry_manager = MockManager()
    posthog_manager = MockManager()
    performance_monitor = MockManager()
    structured_logger = MockManager()
    def track_event(*args, **kwargs): pass
    def set_user_context(*args, **kwargs): pass

try:
    from .security import security_manager, add_security_headers
except ImportError:
    class MockSecurityManager:
        def get_client_ip(self, request):
            return request.client.host if request.client else "unknown"
        async def authenticate_request(self, request):
            return None
    
    security_manager = MockSecurityManager()
    def add_security_headers(response, request):
        return response

logger = logging.getLogger(__name__)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Comprehensive observability middleware"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()
        
        # Extract request information
        method = request.method
        path = request.url.path
        client_ip = security_manager.get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        
        # Get request size
        request_size = int(request.headers.get("content-length", 0))
        
        # Initialize response variables
        response = None
        status_code = 500
        response_size = 0
        user_id = None
        error = None
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
            # Get response size
            if hasattr(response, 'body'):
                response_size = len(response.body)
            
            # Extract user ID from response if available
            user_id = getattr(request.state, 'user_id', None)
            
        except Exception as e:
            error = str(e)
            status_code = 500
            
            # Create error response
            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
            
            # Capture exception
            sentry_manager.capture_exception(e, {
                "request_path": path,
                "request_method": method,
                "client_ip": client_ip,
                "user_agent": user_agent
            })
        
        finally:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Add security headers
            if response:
                response = add_security_headers(response, request)
            
            # Log request
            structured_logger.log_api_request(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_id=user_id,
                request_size=request_size,
                response_size=response_size
            )
            
            # Track in PostHog (for API usage analytics)
            if user_id:
                track_event(user_id, "api_request", {
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "success": status_code < 400
                })
            
            # Record performance metrics
            with performance_monitor.measure_operation(f"api_{method.lower()}_{path.replace('/', '_')}"):
                pass  # Just for recording the metric
        
        return response

class UserContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set user context for observability"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Try to extract user information from token
        try:
            from .security import security_manager
            user_data = await security_manager.authenticate_request(request)
            
            if user_data:
                user_id = user_data["user_id"]
                username = user_data["username"]
                
                # Set user context for observability
                set_user_context(user_id, username)
                
                # Store in request state for other middleware
                request.state.user_id = user_id
                request.state.username = username
        
        except Exception:
            # Don't fail on user context extraction
            pass
        
        response = await call_next(request)
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Log error details
            logger.error(f"Unhandled error in {request.method} {request.url.path}: {str(e)}")
            
            # Capture in Sentry
            sentry_manager.capture_exception(e, {
                "request_method": request.method,
                "request_path": request.url.path,
                "request_headers": dict(request.headers),
                "client_ip": security_manager.get_client_ip(request)
            })
            
            # Return generic error response (don't expose internal errors)
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "error_id": getattr(e, 'error_id', None)
                }
            )

# Health check endpoint functions
async def get_system_health() -> dict:
    """Get comprehensive system health status"""
    from .observability import get_observability_health
    
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "observability": get_observability_health(),
            "performance": performance_monitor.get_performance_summary()
        }
    }
    
    # Check if any critical services are down
    observability = health_data["services"]["observability"]
    if not observability["sentry"]["enabled"] and sentry_manager.initialized:
        health_data["status"] = "degraded"
        health_data["issues"] = ["Sentry error tracking unavailable"]
    
    return health_data