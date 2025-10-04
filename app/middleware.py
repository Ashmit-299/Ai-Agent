#!/usr/bin/env python3
"""
Authentication and Security Middleware
"""

import time
import json
import logging
import uuid
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException, status
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
    from .security import SecurityManager, log_security_event, add_security_headers
    security_manager = SecurityManager()
except ImportError:
    class MockSecurityManager:
        def get_client_ip(self, request):
            return request.client.host if request.client else "unknown"
        async def authenticate_request(self, request):
            return None
    
    security_manager = MockSecurityManager()
    def log_security_event(*args, **kwargs): pass
    def add_security_headers(response, request):
        return response

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Authentication middleware with endpoint protection"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        
        # Define protected endpoints (require authentication)
        self.protected_endpoints = {
            "/upload",
            "/generate-video", 
            "/feedback",
            "/recommend-tags",
            "/users/profile",
            "/users/logout",
            "/monitoring-status",
            "/test-monitoring",
            "/logs",
            "/system-logs",
            "/tasks/",
            "/bucket/cleanup",
            "/bucket/rotate-logs",
            "/maintenance/"
        }
        
        # Define public endpoints (no authentication required)
        self.public_endpoints = {
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc", 
            "/",
            "/test",
            "/demo-login",
            "/debug-auth",
            "/users/register",
            "/users/login",
            "/users/refresh",
            "/contents",
            "/content/",
            "/download/",
            "/stream/",
            "/average-rating/"
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Add request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get client info
        client_ip = security_manager.get_client_ip(request)
        path = request.url.path
        method = request.method
        
        start_time = time.time()
        
        try:
            # Check if endpoint requires authentication
            requires_auth = self._requires_authentication(path)
            user_data = None
            
            if requires_auth:
                try:
                    user_data = await security_manager.authenticate_request(request)
                    if not user_data:
                        log_security_event(
                            "authentication_required",
                            {"path": path, "method": method},
                            client_ip
                        )
                        return JSONResponse(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            content={
                                "detail": "Authentication required",
                                "error_code": "AUTH_REQUIRED",
                                "path": path,
                                "request_id": request_id
                            },
                            headers={"WWW-Authenticate": "Bearer"}
                        )
                    
                    # Add user info to request state
                    request.state.user = user_data
                    request.state.authenticated = True
                    
                    log_security_event(
                        "authenticated_request",
                        {
                            "user_id": user_data["user_id"],
                            "path": path,
                            "method": method
                        },
                        client_ip,
                        user_data["user_id"]
                    )
                    
                except HTTPException as auth_error:
                    log_security_event(
                        "authentication_failed",
                        {
                            "path": path,
                            "method": method,
                            "error": str(auth_error.detail)
                        },
                        client_ip
                    )
                    return JSONResponse(
                        status_code=auth_error.status_code,
                        content={
                            "detail": auth_error.detail,
                            "error_code": "AUTH_FAILED", 
                            "path": path,
                            "request_id": request_id
                        },
                        headers=auth_error.headers or {}
                    )
            else:
                # For public endpoints, try to get user info but don't require it
                try:
                    user_data = await security_manager.authenticate_request(request)
                    if user_data:
                        request.state.user = user_data
                        request.state.authenticated = True
                    else:
                        request.state.authenticated = False
                except:
                    request.state.authenticated = False
            
            # Add security headers
            response = await call_next(request)
            
            # Add security headers to response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            
            # Add HSTS header for HTTPS
            if request.url.scheme == "https":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            
            # Log successful request
            process_time = time.time() - start_time
            
            if user_data:
                try:
                    from core.system_logger import log_api_request
                    log_api_request(path, method, user_data["user_id"], {
                        "status_code": response.status_code,
                        "process_time": round(process_time, 3),
                        "request_id": request_id
                    })
                except ImportError:
                    pass
            
            return response
            
        except Exception as e:
            logger.error(f"Middleware error: {e}")
            log_security_event(
                "middleware_error",
                {"path": path, "method": method, "error": str(e)},
                client_ip
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "error_code": "MIDDLEWARE_ERROR",
                    "request_id": request_id
                }
            )
    
    def _requires_authentication(self, path: str) -> bool:
        """Check if path requires authentication"""
        # Check public endpoints first
        for public_path in self.public_endpoints:
            if path == public_path or (public_path.endswith("/") and path.startswith(public_path)):
                return False
        
        # Check protected endpoints
        for protected_path in self.protected_endpoints:
            if path == protected_path or (protected_path.endswith("/") and path.startswith(protected_path)):
                return True
        
        # Default to requiring authentication for unknown endpoints
        return True

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Request logging middleware with structured JSON output"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extract request info
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        user_agent = request.headers.get("user-agent")
        content_type = request.headers.get("content-type")
        
        # Get user info if available
        user_id = getattr(request.state, 'user', {}).get('user_id', 'anonymous') if hasattr(request.state, 'user') else 'anonymous'
        request_id = getattr(request.state, 'request_id', 'unknown') if hasattr(request.state, 'request_id') else str(uuid.uuid4())
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            # Log request in structured JSON format
            log_data = {
                "timestamp": time.time(),
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "user_id": user_id,
                "status_code": response.status_code,
                "process_time_seconds": round(process_time, 3),
                "user_agent": user_agent,
                "content_type": content_type,
                "response_size": response.headers.get("content-length"),
                "level": "INFO"
            }
            
            # Log to structured JSON sink
            logger.info("API_REQUEST", extra={"json_fields": log_data})
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error request
            error_log_data = {
                "timestamp": time.time(),
                "request_id": request_id,
                "method": method,
                "path": path,
                "user_id": user_id,
                "error": str(e),
                "process_time_seconds": round(process_time, 3),
                "level": "ERROR"
            }
            
            logger.error("API_REQUEST_ERROR", extra={"json_fields": error_log_data})
            
            raise

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Input validation and sanitization middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                max_size = 100 * 1024 * 1024  # 100MB
                if size > max_size:
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"Request too large. Maximum size: {max_size} bytes",
                            "error_code": "REQUEST_TOO_LARGE"
                        }
                    )
            except ValueError:
                pass
        
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-host",
            "x-real-ip", 
            "x-forwarded-for"
        ]
        
        for header in suspicious_headers:
            value = request.headers.get(header, "")
            if any(char in value for char in ['<', '>', '"', "'", '\0']):
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "detail": "Invalid header value",
                        "error_code": "INVALID_HEADER"
                    }
                )
        
        return await call_next(request)

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