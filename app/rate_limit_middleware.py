#!/usr/bin/env python3
"""
Rate limiting middleware for FastAPI
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .rate_limiting import rate_limiter
import logging

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to add rate limit headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers if they were set during request processing
        if hasattr(request.state, 'rate_limit_headers'):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
        
        return response