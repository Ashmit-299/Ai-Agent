#!/usr/bin/env python3
"""
Enhanced Input Validation Middleware - Production Ready
Enforces file size limits, request body restrictions, and input sanitization
"""

import os
import hashlib
from fastapi import Request, HTTPException, UploadFile
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, List, Dict, Any
import json
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try to import python-magic for MIME type detection
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    logger.warning("python-magic not available. Install with: pip install python-magic")

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Enhanced input validation middleware with comprehensive security"""
    
    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB default
        super().__init__(app)
        self.max_body_size = max_body_size
        
    async def dispatch(self, request: Request, call_next):
        # Check content length before processing
        content_length = request.headers.get('content-length')
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_body_size:
                logger.warning(f"Request body too large: {content_length} bytes from {request.client.host}")
                raise HTTPException(
                    status_code=413,
                    detail=f"Request body too large. Maximum allowed: {self.max_body_size // 1024 // 1024}MB"
                )
        
        # Add request size tracking
        request.state.content_length = content_length or 0
        
        response = await call_next(request)
        return response

class FileValidator:
    """Comprehensive file validation with security checks"""
    
    ALLOWED_FILE_TYPES = {
        'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
        'video': ['video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo'],
        'audio': ['audio/mpeg', 'audio/wav', 'audio/ogg'],
        'document': ['application/pdf', 'text/plain', 'application/msword'],
        'text': ['text/plain', 'text/markdown']
    }
    
    DANGEROUS_EXTENSIONS = {
        '.exe', '.scr', '.bat', '.cmd', '.com', '.pif', '.vbs', '.js', '.jar',
        '.app', '.deb', '.pkg', '.dmg', '.iso', '.msi', '.dll', '.sys'
    }
    
    MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE_MB', '100')) * 1024 * 1024  # 100MB default
    
    @classmethod
    async def validate_file(cls, file: UploadFile, allowed_categories: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive file validation with security checks
        
        Args:
            file: UploadFile object to validate
            allowed_categories: List of allowed file categories
            
        Returns:
            Dict with validation results
            
        Raises:
            HTTPException: If file validation fails
        """
        validation_result = {
            'filename': file.filename,
            'size': 0,
            'mime_type': None,
            'file_hash': None,
            'is_safe': True,
            'warnings': []
        }
        
        # Read file content
        content = await file.read()
        await file.seek(0)  # Reset file pointer
        
        validation_result['size'] = len(content)
        
        # 1. File size validation
        if validation_result['size'] > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed: {cls.MAX_FILE_SIZE // 1024 // 1024}MB, "
                       f"received: {validation_result['size'] // 1024 // 1024}MB"
            )
        
        # 2. Empty file check
        if validation_result['size'] == 0:
            raise HTTPException(status_code=400, detail="Empty file not allowed")
        
        # 3. Filename validation
        if not file.filename or len(file.filename) > 255:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # 4. Dangerous extension check
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext in cls.DANGEROUS_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Dangerous file extension not allowed: {file_ext}"
            )
        
        # 5. MIME type validation using magic bytes (if available)
        if MAGIC_AVAILABLE:
            try:
                mime_type = magic.from_buffer(content[:2048], mime=True)
                validation_result['mime_type'] = mime_type
            except Exception as e:
                logger.warning(f"Could not determine MIME type: {e}")
                validation_result['warnings'].append("Could not determine MIME type")
        else:
            # Fallback: use file extension to guess MIME type
            mime_map = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
                '.gif': 'image/gif', '.webp': 'image/webp',
                '.mp4': 'video/mp4', '.avi': 'video/x-msvideo', '.mov': 'video/quicktime',
                '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg',
                '.pdf': 'application/pdf', '.txt': 'text/plain', '.md': 'text/markdown'
            }
            validation_result['mime_type'] = mime_map.get(file_ext, 'application/octet-stream')
            validation_result['warnings'].append("MIME type guessed from extension")
        
        # 6. Category validation
        if allowed_categories and validation_result['mime_type']:
            allowed_mimes = []
            for category in allowed_categories:
                allowed_mimes.extend(cls.ALLOWED_FILE_TYPES.get(category, []))
            
            if validation_result['mime_type'] not in allowed_mimes:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed types: {allowed_mimes}"
                )
        
        # 7. File hash for integrity
        validation_result['file_hash'] = hashlib.sha256(content).hexdigest()
        
        # 8. Basic malware signature check (simple patterns)
        malware_patterns = [
            b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR',  # EICAR test signature
            b'TVqQAAMAAAAEAAAA',  # PE executable header
            b'MZ',  # DOS executable header
        ]
        
        for pattern in malware_patterns:
            if pattern in content[:1024]:
                raise HTTPException(
                    status_code=400,
                    detail="File contains suspicious content"
                )
        
        logger.info(f"File validation passed: {file.filename} ({validation_result['size']} bytes)")
        return validation_result

class TextValidator:
    """Text input validation and sanitization"""
    
    # XSS prevention patterns
    XSS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
    ]
    
    # SQL injection patterns
    SQL_PATTERNS = [
        re.compile(r'\b(union|select|insert|update|delete|drop|create|alter)\b', re.IGNORECASE),
        re.compile(r'[\'""];.*(\sor\s|\sand\s)', re.IGNORECASE),
        re.compile(r'--.*$', re.MULTILINE),
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 10000, allow_html: bool = False) -> str:
        """
        Sanitize text input to prevent XSS and injection attacks
        
        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags
            
        Returns:
            Sanitized text
            
        Raises:
            HTTPException: If text validation fails
        """
        if not text:
            return ""
        
        # Length validation
        if len(text) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Text too long. Maximum allowed: {max_length} characters"
            )
        
        # XSS prevention
        if not allow_html:
            for pattern in cls.XSS_PATTERNS:
                if pattern.search(text):
                    raise HTTPException(
                        status_code=400,
                        detail="Text contains potentially dangerous HTML/JavaScript"
                    )
        
        # Basic SQL injection prevention
        for pattern in cls.SQL_PATTERNS:
            if pattern.search(text):
                logger.warning(f"Potential SQL injection attempt detected: {text[:100]}...")
                raise HTTPException(
                    status_code=400,
                    detail="Text contains potentially dangerous SQL patterns"
                )
        
        # Remove null bytes and control characters
        sanitized = text.replace('\x00', '').replace('\r', '').strip()
        
        # Basic HTML entity encoding if HTML not allowed
        if not allow_html:
            sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
            sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
        
        return sanitized
    
    @classmethod
    def validate_json_input(cls, data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """
        Validate and sanitize JSON input data
        
        Args:
            data: Input dictionary to validate
            max_depth: Maximum nesting depth allowed
            
        Returns:
            Validated and sanitized data
        """
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                raise HTTPException(
                    status_code=400,
                    detail=f"JSON too deeply nested. Maximum depth: {max_depth}"
                )
            
            if isinstance(obj, dict):
                return {
                    key: check_depth(value, current_depth + 1)
                    for key, value in obj.items()
                }
            elif isinstance(obj, list):
                return [check_depth(item, current_depth + 1) for item in obj]
            elif isinstance(obj, str):
                return cls.sanitize_text(obj)
            else:
                return obj
        
        return check_depth(data)

# Validation decorators for endpoints
def validate_file_upload(allowed_categories: List[str] = None, max_files: int = 1):
    """Decorator for file upload validation"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract file parameters
            files = []
            for key, value in kwargs.items():
                if isinstance(value, UploadFile):
                    files.append(value)
                elif isinstance(value, list) and all(isinstance(f, UploadFile) for f in value):
                    files.extend(value)
            
            # Validate file count
            if len(files) > max_files:
                raise HTTPException(
                    status_code=400,
                    detail=f"Too many files. Maximum allowed: {max_files}"
                )
            
            # Validate each file
            for file in files:
                await FileValidator.validate_file(file, allowed_categories)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def validate_text_input(max_length: int = 10000):
    """Decorator for text input validation"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Sanitize string parameters
            for key, value in kwargs.items():
                if isinstance(value, str):
                    kwargs[key] = TextValidator.sanitize_text(value, max_length)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator