#!/usr/bin/env python3
"""
Global Authentication Middleware
Enforces authentication on all endpoints except specified public ones
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import re

class GlobalAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce authentication on all endpoints except public ones"""
    
    def __init__(self, app):
        super().__init__(app)
        # Define public endpoints that don't require authentication
        self.public_paths = {
            "/health",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/docs/oauth2-redirect",
            "/users/login",
            "/users/register", 
            "/demo-login"
        }
        
        # Regex patterns for public paths
        self.public_patterns = [
            r"^/docs.*",
            r"^/redoc.*",
            r"^/openapi\.json$"
        ]
    
    def is_public_path(self, path: str) -> bool:
        """Check if path is public and doesn't require authentication"""
        # Exact match
        if path in self.public_paths:
            return True
            
        # Pattern match
        for pattern in self.public_patterns:
            if re.match(pattern, path):
                return True
                
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Process request and enforce authentication"""
        path = request.url.path
        
        # Skip authentication for public paths
        if self.is_public_path(path):
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
        
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication format. Use Bearer token"}
            )
        
        # Extract token
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token missing"}
            )
        
        # Validate token (basic check - detailed validation happens in endpoints)
        try:
            # Import here to avoid circular imports
            from .auth import verify_token
            
            # Basic token validation
            payload = verify_token(token)
            if not payload:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Invalid or expired token"}
                )
                
        except Exception as e:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token validation failed"}
            )
        
        # Continue to endpoint
        return await call_next(request)