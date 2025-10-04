#!/usr/bin/env python3
"""
Request ID and Structured Logging Middleware
"""
import uuid
import time
import json
import logging
import os
from typing import Dict, Any, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request"""
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        
        # Add to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Structured JSON logging for all requests"""
    
    def __init__(self, app, logger_name: str = "api"):
        super().__init__(app)
        self.logger = logging.getLogger(logger_name)
        
        # Configure JSON formatter if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = JsonFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (common in production)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
            
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request if available"""
        try:
            # Check if user is attached to request state
            if hasattr(request.state, 'user'):
                user = request.state.user
                if hasattr(user, 'user_id'):
                    return user.user_id
                elif isinstance(user, dict):
                    return user.get('user_id')
            
            # Try to extract from Authorization header
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
                if token.startswith("simple_token_"):
                    parts = token.split("_")
                    if len(parts) >= 3:
                        return parts[2]
            
            return None
        except Exception:
            return None
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Get request details
        request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
        client_ip = self.get_client_ip(request)
        user_id = self.get_user_id(request)
        
        # Log request start
        request_log = {
            "event": "request_start",
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", "unknown"),
            "user_id": user_id,
            "timestamp": time.time()
        }
        
        self.logger.info("Request started", extra=request_log)
        
        # Process request
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Log successful response
            response_log = {
                "event": "request_complete",
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time_ms": round(processing_time * 1000, 2),
                "user_id": user_id,
                "client_ip": client_ip,
                "timestamp": time.time()
            }
            
            self.logger.info("Request completed", extra=response_log)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            
            # Log error
            error_log = {
                "event": "request_error",
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time_ms": round(processing_time * 1000, 2),
                "user_id": user_id,
                "client_ip": client_ip,
                "timestamp": time.time()
            }
            
            self.logger.error("Request failed", extra=error_log)
            raise

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        # Create base log entry
        log_entry = {
            "timestamp": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        
        # Add extra fields if present
        if hasattr(record, '__dict__'):
            for key, value in record.__dict__.items():
                if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 
                              'pathname', 'filename', 'module', 'lineno', 
                              'funcName', 'created', 'msecs', 'relativeCreated',
                              'thread', 'threadName', 'processName', 'process',
                              'stack_info', 'exc_info', 'exc_text', 'getMessage']:
                    log_entry[key] = value
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str)

# Audit logging helper
class AuditLogger:
    """Helper for audit logging"""
    
    def __init__(self):
        self.logger = logging.getLogger("audit")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = JsonFormatter()
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_action(self, 
                   user_id: Optional[str],
                   action: str,
                   resource_type: str,
                   resource_id: str,
                   request_id: Optional[str] = None,
                   ip_address: Optional[str] = None,
                   details: Optional[Dict[str, Any]] = None,
                   status: str = "success"):
        """Log audit event"""
        
        audit_entry = {
            "event": "audit_log",
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "request_id": request_id,
            "ip_address": ip_address,
            "details": details or {},
            "status": status,
            "timestamp": time.time()
        }
        
        self.logger.info(f"Audit: {action}", extra=audit_entry)
        
        # Also save to database if available
        try:
            self._save_to_database(audit_entry)
        except Exception as e:
            self.logger.error(f"Failed to save audit log to database: {e}")
    
    def _save_to_database(self, audit_entry: Dict[str, Any]):
        """Save audit entry to database"""
        try:
            from core.database import DatabaseManager
            import psycopg2
            
            DATABASE_URL = os.getenv("DATABASE_URL")
            if 'postgresql' in DATABASE_URL:
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                cur.execute("""
                    INSERT INTO audit_logs 
                    (user_id, action, resource_type, resource_id, timestamp, ip_address, request_id, details, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    audit_entry.get('user_id'),
                    audit_entry.get('action'),
                    audit_entry.get('resource_type'),
                    audit_entry.get('resource_id'),
                    audit_entry.get('timestamp'),
                    audit_entry.get('ip_address'),
                    audit_entry.get('request_id'),
                    json.dumps(audit_entry.get('details', {})),
                    audit_entry.get('status')
                ))
                
                conn.commit()
                cur.close()
                conn.close()
                
        except Exception as e:
            # Don't fail the request if audit logging fails
            pass

# Global audit logger instance
audit_logger = AuditLogger()