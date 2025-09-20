# app/security.py
import hashlib
import hmac
import time
import logging
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException, status
from datetime import datetime
import os

# JWT imports with fallback
try:
    from jose import JWTError, jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    import base64

# Structured logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
security_logger = logging.getLogger('security')
rate_limit_logger = logging.getLogger('rate_limit')

security = HTTPBearer()

# Security configuration - Use environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_that_should_be_changed_in_production_and_is_at_least_32_bytes_long")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Rate limiting
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 3600  # 1 hour

class SecurityManager:
    def __init__(self):
        self.rate_limit_store: Dict[str, list] = {}
        self.security = HTTPBearer(auto_error=False)
        self.failed_attempts: Dict[str, int] = {}
        self.blocked_ips: Dict[str, float] = {}
    
    def create_access_token(self, data: dict, expires_delta: Optional[int] = None):
        """Create JWT access token with logging"""
        to_encode = data.copy()
        if expires_delta:
            expire = time.time() + expires_delta
        else:
            expire = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        
        to_encode.update({"exp": expire})
        
        if JWT_AVAILABLE:
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        else:
            # Fallback token creation
            token_data = json.dumps(to_encode, default=str)
            encoded_jwt = base64.b64encode(token_data.encode()).decode()
        
        security_logger.info(f"Token created for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token with logging"""
        try:
            if JWT_AVAILABLE:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            else:
                # Fallback token verification
                token_data = base64.b64decode(token.encode()).decode()
                payload = json.loads(token_data)
                # Check expiration
                if payload.get('exp', 0) < time.time():
                    raise HTTPException(status_code=401, detail="Token expired")
            
            return payload
        except HTTPException:
            raise
        except Exception as e:
            security_logger.warning(f"Token verification failed: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Enhanced rate limiting with logging and IP blocking"""
        current_time = time.time()
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            if current_time < self.blocked_ips[client_ip]:
                rate_limit_logger.warning(f"Blocked IP attempted access: {client_ip}")
                return False
            else:
                # Unblock IP
                del self.blocked_ips[client_ip]
                if client_ip in self.failed_attempts:
                    del self.failed_attempts[client_ip]
        
        # Clean old entries
        self.rate_limit_store = {
            ip: requests for ip, requests in self.rate_limit_store.items()
            if any(req_time > current_time - RATE_LIMIT_WINDOW for req_time in requests)
        }
        
        # Check current client
        if client_ip not in self.rate_limit_store:
            self.rate_limit_store[client_ip] = []
        
        # Remove old requests for this client
        self.rate_limit_store[client_ip] = [
            req_time for req_time in self.rate_limit_store[client_ip]
            if req_time > current_time - RATE_LIMIT_WINDOW
        ]
        
        # Check if limit exceeded
        if len(self.rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
            # Track failed attempts
            self.failed_attempts[client_ip] = self.failed_attempts.get(client_ip, 0) + 1
            
            # Block IP after multiple violations
            if self.failed_attempts[client_ip] >= 3:
                self.blocked_ips[client_ip] = current_time + 3600  # Block for 1 hour
                rate_limit_logger.error(f"IP blocked for repeated violations: {client_ip}")
            
            rate_limit_logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return False
        
        # Add current request
        self.rate_limit_store[client_ip].append(current_time)
        return True
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], client_ip: str = "unknown"):
        """Log security events with structured data"""
        event_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "client_ip": client_ip,
            "details": details
        }
        security_logger.info(json.dumps(event_data))
    
    def get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

# Global security manager instance
security_manager = SecurityManager()

def rate_limit_middleware(request: Request):
    """Enhanced rate limiting middleware with logging"""
    client_ip = security_manager.get_client_ip(request)
    
    if not security_manager.check_rate_limit(client_ip):
        security_manager.log_security_event(
            "RATE_LIMIT_EXCEEDED",
            {"path": str(request.url.path), "method": request.method},
            client_ip
        )
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Log successful requests (sample 1% to avoid log spam)
    import random
    if random.random() < 0.01:
        security_manager.log_security_event(
            "REQUEST_ALLOWED",
            {"path": str(request.url.path), "method": request.method},
            client_ip
        )

def hash_password(password: str) -> str:
    """Hash password using PBKDF2 (secure algorithm)"""
    import hashlib
    import os
    
    # Generate a random salt
    salt = os.urandom(32)
    # Use PBKDF2 with SHA-256
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    # Return salt + hash as hex
    return salt.hex() + pwdhash.hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against PBKDF2 hash"""
    import hashlib
    
    try:
        # Extract salt (first 64 chars) and hash (remaining)
        salt = bytes.fromhex(hashed[:64])
        stored_hash = hashed[64:]
        
        # Hash the provided password with the same salt
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        
        # Compare hashes
        return hmac.compare_digest(pwdhash.hex(), stored_hash)
    except (ValueError, IndexError):
        return False

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = security_manager.verify_token(token.credentials)
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")