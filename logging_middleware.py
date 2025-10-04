
# Enhanced logging middleware for requests, errors, and feedback
import time
import json
from datetime import datetime

async def log_request_middleware(request: Request, call_next):
    """Log all requests, errors, and feedback events"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request
    try:
        from core.database import DatabaseManager
        DatabaseManager.save_system_log(
            level="INFO",
            message=f"Request: {request.method} {request.url.path}",
            module="api_request",
            user_id=getattr(request.state, 'user_id', None)
        )
    except Exception:
        pass
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        # Log response
        DatabaseManager.save_system_log(
            level="INFO" if response.status_code < 400 else "ERROR",
            message=f"Response: {response.status_code} in {duration:.2f}ms",
            module="api_response"
        )
        
        return response
        
    except Exception as e:
        # Log errors
        DatabaseManager.save_system_log(
            level="ERROR",
            message=f"Request failed: {str(e)}",
            module="api_error"
        )
        raise
