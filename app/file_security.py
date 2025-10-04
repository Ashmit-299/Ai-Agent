#!/usr/bin/env python3
"""
Secure file upload validation and handling
"""

import os
import mimetypes
import hashlib
from typing import List, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from pathlib import Path

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

# Allowed file types and their MIME types
ALLOWED_FILE_TYPES = {
    # Text files
    '.txt': ['text/plain'],
    '.md': ['text/markdown', 'text/plain'],
    '.json': ['application/json', 'text/plain'],
    '.csv': ['text/csv', 'application/csv'],
    
    # Image files (for content analysis)
    '.jpg': ['image/jpeg'],
    '.jpeg': ['image/jpeg'],
    '.png': ['image/png'],
    '.gif': ['image/gif'],
    '.webp': ['image/webp'],
    
    # Document files
    '.pdf': ['application/pdf'],
    '.doc': ['application/msword'],
    '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
    
    # Video files (for processing)
    '.mp4': ['video/mp4'],
    '.avi': ['video/x-msvideo'],
    '.mov': ['video/quicktime'],
    '.webm': ['video/webm']
}

# Maximum file sizes by type (in bytes)
MAX_FILE_SIZES = {
    'text': 10 * 1024 * 1024,      # 10MB for text files
    'image': 50 * 1024 * 1024,     # 50MB for images
    'document': 100 * 1024 * 1024, # 100MB for documents
    'video': 500 * 1024 * 1024     # 500MB for videos
}

# File type categories
FILE_CATEGORIES = {
    'text': ['.txt', '.md', '.json', '.csv'],
    'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
    'document': ['.pdf', '.doc', '.docx'],
    'video': ['.mp4', '.avi', '.mov', '.webm']
}

class FileSecurityValidator:
    """Secure file upload validator"""
    
    @staticmethod
    def validate_filename(filename: str) -> str:
        """Validate and sanitize filename"""
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename cannot be empty"
            )
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Check for dangerous patterns
        dangerous_patterns = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*', '\0']
        for pattern in dangerous_patterns:
            if pattern in filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Filename contains invalid characters: {pattern}"
                )
        
        # Check filename length
        if len(filename) > 255:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filename too long (max 255 characters)"
            )
        
        # Ensure file has extension
        if '.' not in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must have an extension"
            )
        
        return filename
    
    @staticmethod
    def validate_file_extension(filename: str) -> str:
        """Validate file extension"""
        ext = Path(filename).suffix.lower()
        
        if ext not in ALLOWED_FILE_TYPES:
            allowed_exts = ', '.join(ALLOWED_FILE_TYPES.keys())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {allowed_exts}"
            )
        
        return ext
    
    @staticmethod
    def validate_mime_type(file_content: bytes, filename: str) -> bool:
        """Validate MIME type using file content"""
        ext = Path(filename).suffix.lower()
        allowed_mimes = ALLOWED_FILE_TYPES.get(ext, [])
        
        detected_mime = None
        
        if MAGIC_AVAILABLE and magic:
            try:
                # Use python-magic to detect actual MIME type
                detected_mime = magic.from_buffer(file_content, mime=True)
            except Exception:
                pass
        
        if not detected_mime:
            # Fallback to mimetypes module
            detected_mime, _ = mimetypes.guess_type(filename)
        
        if detected_mime and detected_mime not in allowed_mimes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File content doesn't match expected type. Expected: {allowed_mimes}, Got: {detected_mime}"
            )
        
        return True
    
    @staticmethod
    def validate_file_size(file_size: int, filename: str) -> bool:
        """Validate file size based on type"""
        ext = Path(filename).suffix.lower()
        
        # Determine file category
        category = None
        for cat, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                category = cat
                break
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unknown file category"
            )
        
        max_size = MAX_FILE_SIZES.get(category, 10 * 1024 * 1024)  # Default 10MB
        
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size for {category} files: {max_size_mb:.1f}MB"
            )
        
        return True
    
    @staticmethod
    def scan_for_malicious_content(file_content: bytes, filename: str) -> bool:
        """Basic malicious content scanning"""
        ext = Path(filename).suffix.lower()
        
        # For text files, check for suspicious patterns
        if ext in ['.txt', '.md', '.json', '.csv']:
            try:
                text_content = file_content.decode('utf-8', errors='ignore').lower()
                
                # Check for script injection patterns
                suspicious_patterns = [
                    '<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=',
                    'eval(', 'exec(', 'system(', 'shell_exec', 'passthru',
                    '<?php', '<%', 'import os', 'import subprocess'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in text_content:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File contains suspicious content: {pattern}"
                        )
            except UnicodeDecodeError:
                # If we can't decode as text, that's suspicious for text files
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Text file contains invalid characters"
                )
        
        return True
    
    @staticmethod
    def generate_secure_filename(original_filename: str, user_id: str = None) -> str:
        """Generate secure filename with hash"""
        # Validate original filename
        safe_filename = FileSecurityValidator.validate_filename(original_filename)
        ext = Path(safe_filename).suffix.lower()
        
        # Generate hash of filename + timestamp + user_id
        import time
        hash_input = f"{safe_filename}_{time.time()}_{user_id or 'anonymous'}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        
        # Create secure filename
        timestamp = int(time.time())
        secure_filename = f"{timestamp}_{file_hash}_{safe_filename}"
        
        return secure_filename
    
    @classmethod
    async def validate_upload_file(cls, file: UploadFile, user_id: str = None) -> Tuple[str, bytes]:
        """Complete file validation pipeline"""
        # Validate filename
        safe_filename = cls.validate_filename(file.filename)
        
        # Validate extension
        ext = cls.validate_file_extension(safe_filename)
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size
        cls.validate_file_size(len(file_content), safe_filename)
        
        # Validate MIME type
        cls.validate_mime_type(file_content, safe_filename)
        
        # Scan for malicious content
        cls.scan_for_malicious_content(file_content, safe_filename)
        
        # Generate secure filename
        secure_filename = cls.generate_secure_filename(safe_filename, user_id)
        
        # Reset file pointer for further processing
        await file.seek(0)
        
        return secure_filename, file_content

def create_secure_upload_directory(base_path: str = "uploads") -> str:
    """Create secure upload directory with proper permissions"""
    upload_dir = Path(base_path)
    upload_dir.mkdir(exist_ok=True, mode=0o755)
    
    # Create .htaccess file to prevent direct access (for Apache)
    htaccess_path = upload_dir / ".htaccess"
    if not htaccess_path.exists():
        with open(htaccess_path, 'w') as f:
            f.write("deny from all\n")
    
    return str(upload_dir)

def save_file_securely(file_content: bytes, filename: str, upload_dir: str = "uploads") -> str:
    """Save file securely to upload directory"""
    # Ensure upload directory exists
    secure_dir = create_secure_upload_directory(upload_dir)
    
    # Create full file path
    file_path = Path(secure_dir) / filename
    
    # Ensure we're not writing outside the upload directory
    if not str(file_path.resolve()).startswith(str(Path(secure_dir).resolve())):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file path"
        )
    
    # Write file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    # Set secure permissions
    os.chmod(file_path, 0o644)
    
    return str(file_path)

# Usage example function
async def secure_file_upload_handler(file: UploadFile, user_id: str = None) -> dict:
    """Example secure file upload handler"""
    try:
        # Validate file
        secure_filename, file_content = await FileSecurityValidator.validate_upload_file(file, user_id)
        
        # Save file securely
        file_path = save_file_securely(file_content, secure_filename)
        
        return {
            "status": "success",
            "original_filename": file.filename,
            "secure_filename": secure_filename,
            "file_path": file_path,
            "file_size": len(file_content),
            "content_type": file.content_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(e)}"
        )