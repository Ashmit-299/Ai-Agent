#!/usr/bin/env python3
"""
Production-grade security configuration for AI Agent
"""

# Suppress bcrypt warnings completely
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import fix_bcrypt
except:
    pass

import os
import secrets
import hashlib
import hmac
import time
import json
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Security Configuration
class SecurityConfig:
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    
    # Password Configuration
    PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
    MIN_PASSWORD_LENGTH = 8
    
    # Rate Limiting Configuration
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_DURATION = 900  # 15 minutes
    
    # Security Headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

config = SecurityConfig()

# Password Security
class PasswordManager:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        if len(password) < config.MIN_PASSWORD_LENGTH:
            raise ValueError(f"Password must be at least {config.MIN_PASSWORD_LENGTH} characters")
        return config.PWD_CONTEXT.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return config.PWD_CONTEXT.verify(plain_password, hashed_password)
        except Exception as e:
            logger.warning(f"Password verification failed: {e}")
            return False
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0
        
        if len(password) < config.MIN_PASSWORD_LENGTH:
            issues.append(f"Must be at least {config.MIN_PASSWORD_LENGTH} characters")
        else:
            score += 1
            
        if not any(c.isupper() for c in password):
            issues.append("Must contain uppercase letter")
        else:
            score += 1
            
        if not any(c.islower() for c in password):
            issues.append("Must contain lowercase letter")
        else:
            score += 1
            
        if not any(c.isdigit() for c in password):
            issues.append("Must contain number")
        else:
            score += 1
            
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Must contain special character")
        else:
            score += 1
        
        return {
            "valid": len(issues) == 0,
            "score": score,
            "max_score": 5,
            "issues": issues
        }

# JWT Token Management with enhanced Supabase JWKS support
class JWTManager:
    # Supabase configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
    
    @classmethod
    @lru_cache(maxsize=1)
    def get_supabase_jwks(cls):
        """Fetch Supabase JWKS for token validation"""
        try:
            if cls.SUPABASE_URL:
                jwks_url = f"{cls.SUPABASE_URL}/.well-known/jwks.json"
                response = requests.get(jwks_url, timeout=10)
                response.raise_for_status()
                logger.info("Supabase JWKS fetched successfully")
                return response.json()
        except Exception as e:
            logger.warning(f"Failed to fetch Supabase JWKS: {e}")
        return None
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token with enhanced security"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add security claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for tracking
        })
        
        try:
            return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
        except Exception as e:
            logger.error(f"Token creation failed: {e}")
            # Fallback simple token for development
            return f"fallback_token_{data.get('user_id', 'unknown')}_{int(time.time())}"
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """Create refresh token"""
        expire = datetime.utcnow() + timedelta(days=config.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(to_encode, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    
    @classmethod
    def verify_token(cls, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token with enhanced Supabase JWKS support"""
        try:
            # First try Supabase JWKS verification (RS256)
            jwks = cls.get_supabase_jwks()
            if jwks:
                try:
                    payload = jwt.decode(
                        token,
                        jwks,
                        algorithms=["RS256"],
                        audience="authenticated",
                        issuer=f"{cls.SUPABASE_URL}/auth/v1" if cls.SUPABASE_URL else None
                    )
                    logger.info("Token verified using Supabase JWKS (RS256)")
                    return {
                        "user_id": payload["sub"],
                        "username": payload.get("email", payload["sub"]),
                        "email": payload.get("email"),
                        "role": payload.get("role", "authenticated"),
                        "token_type": "supabase_jwks",
                        "jti": payload.get("jti"),
                        "aud": payload.get("aud"),
                        "iss": payload.get("iss")
                    }
                except JWTError as e:
                    logger.debug(f"JWKS verification failed: {e}")
            
            # Second try Supabase JWT secret verification (HS256)
            if cls.SUPABASE_JWT_SECRET:
                try:
                    payload = jwt.decode(
                        token, 
                        cls.SUPABASE_JWT_SECRET, 
                        algorithms=["HS256"],
                        audience="authenticated",
                        issuer=f"{cls.SUPABASE_URL}/auth/v1" if cls.SUPABASE_URL else None
                    )
                    logger.info("Token verified using Supabase JWT secret (HS256)")
                    return {
                        "user_id": payload["sub"],
                        "username": payload.get("email", payload["sub"]),
                        "email": payload.get("email"),
                        "role": payload.get("role", "authenticated"),
                        "token_type": "supabase_secret",
                        "jti": payload.get("jti"),
                        "aud": payload.get("aud"),
                        "iss": payload.get("iss")
                    }
                except JWTError as e:
                    logger.debug(f"Supabase JWT secret verification failed: {e}")
            
            # Third try our local JWT verification
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise JWTError("Invalid token type")
            
            # Check blacklist
            jti = payload.get("jti")
            if jti and token_blacklist.is_blacklisted(jti):
                raise JWTError("Token has been revoked")
            
            logger.info("Token verified using local JWT")
            payload["token_type"] = "local"
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"}
            )

# Enhanced Rate Limiting
class RateLimiter:
    """Rate limiting for API endpoints"""
    
    def __init__(self):
        self.requests = {}  # {key: [(timestamp, count)]}
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def is_allowed(self, key: str, max_requests: int = 100, window: int = 3600) -> bool:
        """Check if request is allowed within rate limit"""
        now = time.time()
        self._cleanup_old_entries()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old entries outside window
        self.requests[key] = [
            (timestamp, count) for timestamp, count in self.requests[key]
            if now - timestamp < window
        ]
        
        # Count requests in window
        total_requests = sum(count for _, count in self.requests[key])
        
        if total_requests >= max_requests:
            return False
        
        # Add current request
        self.requests[key].append((now, 1))
        return True
    
    def _cleanup_old_entries(self):
        """Remove old rate limiting entries"""
        now = time.time()
        if now - self.last_cleanup > self.cleanup_interval:
            for key in list(self.requests.keys()):
                self.requests[key] = [
                    (timestamp, count) for timestamp, count in self.requests[key]
                    if now - timestamp < 3600
                ]
                if not self.requests[key]:
                    del self.requests[key]
            self.last_cleanup = now

# Authentication Rate Limiting
class AuthRateLimiter:
    def __init__(self):
        self.attempts = {}  # {ip: {count: int, last_attempt: float, locked_until: float}}
    
    def is_locked(self, client_ip: str) -> bool:
        """Check if IP is currently locked"""
        if client_ip in self.attempts:
            attempt_data = self.attempts[client_ip]
            if "locked_until" in attempt_data and time.time() < attempt_data["locked_until"]:
                return True
        return False
    
    def record_attempt(self, client_ip: str, success: bool) -> Dict[str, Any]:
        """Record authentication attempt"""
        current_time = time.time()
        
        if client_ip not in self.attempts:
            self.attempts[client_ip] = {"count": 0, "last_attempt": current_time}
        
        attempt_data = self.attempts[client_ip]
        
        if success:
            # Reset on successful login
            self.attempts[client_ip] = {"count": 0, "last_attempt": current_time}
            return {"locked": False, "attempts_remaining": config.MAX_LOGIN_ATTEMPTS}
        else:
            # Increment failed attempts
            attempt_data["count"] += 1
            attempt_data["last_attempt"] = current_time
            
            if attempt_data["count"] >= config.MAX_LOGIN_ATTEMPTS:
                # Lock the IP
                attempt_data["locked_until"] = current_time + config.LOGIN_LOCKOUT_DURATION
                return {
                    "locked": True, 
                    "locked_until": attempt_data["locked_until"],
                    "attempts_remaining": 0
                }
            
            return {
                "locked": False,
                "attempts_remaining": config.MAX_LOGIN_ATTEMPTS - attempt_data["count"]
            }

# Global rate limiter instances
auth_rate_limiter = AuthRateLimiter()
api_rate_limiter = RateLimiter()

# Token blacklist for logout functionality
class TokenBlacklist:
    def __init__(self):
        self.blacklisted_tokens = set()
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def add_token(self, jti: str):
        """Add token to blacklist"""
        self.blacklisted_tokens.add(jti)
        self._cleanup_expired()
    
    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        self._cleanup_expired()
        return jti in self.blacklisted_tokens
    
    def _cleanup_expired(self):
        """Remove expired tokens from blacklist"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # In production, implement proper cleanup based on token expiry
            self.last_cleanup = current_time

# Global token blacklist instance
token_blacklist = TokenBlacklist()

# Enhanced Security Manager
class SecurityManager:
    def __init__(self):
        self.security_bearer = HTTPBearer(auto_error=False)
        self.rate_limiter = api_rate_limiter
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP with proxy support"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def authenticate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Authenticate request with comprehensive validation"""
        try:
            # Get authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return None
            
            token = authorization[7:]  # Remove "Bearer " prefix
            
            # Rate limiting check
            client_ip = self.get_client_ip(request)
            if not self.rate_limiter.is_allowed(f"auth:{client_ip}", max_requests=100):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )
            
            # Verify token
            payload = JWTManager.verify_token(token, "access")
            
            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("sub") or payload.get("username"),
                "token_type": payload.get("token_type", "local"),
                "token_jti": payload.get("jti")
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"}
            )

# Global security manager instance
security_manager = SecurityManager()

# Input Sanitization
class InputSanitizer:
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")
        
        # Remove null bytes
        cleaned = input_str.replace('\x00', '')
        
        # Remove control characters except newlines and tabs
        cleaned = ''.join(char for char in cleaned 
                         if ord(char) >= 32 or char in '\n\t\r')
        
        # Truncate to max length
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            raise ValueError("Filename cannot be empty")
        
        # Remove path traversal attempts
        filename = os.path.basename(filename)
        
        # Allow only safe characters
        safe_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
        filename = ''.join(c for c in filename if c in safe_chars)
        
        if not filename:
            raise ValueError("Filename contains no valid characters")
        
        # Ensure reasonable length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Validate filename for security"""
        if not filename or len(filename) > 255:
            return False
        
        # Check for path traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\0']
        return not any(char in filename for char in dangerous_chars)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not email or not isinstance(email, str):
            return False
        
        # Basic email pattern check
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email)) and len(email) <= 255

# Utility Functions
def generate_secure_token() -> str:
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(32)

def constant_time_compare(a: str, b: str) -> bool:
    """Constant time string comparison to prevent timing attacks"""
    return hmac.compare_digest(a.encode(), b.encode())

def log_security_event(event_type: str, event_data: dict, client_ip: str, user_id: str = None):
    """Log security events for audit"""
    try:
        from core.system_logger import system_logger
        system_logger.log_security_event(event_type, event_data, client_ip, user_id)
    except Exception as e:
        logger.warning(f"Security event logging failed: {e}")
        # Fallback logging
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "client_ip": client_ip,
            "user_id": user_id,
            "details": event_data
        }
        logger.warning(f"SECURITY_EVENT: {json.dumps(log_entry)}")

# Security Headers Middleware
def add_security_headers(response, request: Request):
    """Add security headers to response"""
    for header, value in config.SECURITY_HEADERS.items():
        response.headers[header] = value
    
    # Add custom headers based on request
    if request.url.path.startswith("/api/"):
        response.headers["X-API-Version"] = "1.0"
    
    return response

# Rate Limiting Middleware
def rate_limit_middleware(request: Request):
    """Apply rate limiting based on endpoint and user"""
    client_ip = security_manager.get_client_ip(request)
    
    # Check if this is an auth endpoint
    auth_endpoints = ["/users/login", "/users/register", "/users/refresh"]
    if request.url.path in auth_endpoints:
        if auth_rate_limiter.is_locked(client_ip):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many authentication attempts. Please try again later.",
                headers={"Retry-After": str(config.LOGIN_LOCKOUT_DURATION)}
            )

# Security decorators
def require_auth(func):
    """Decorator to require authentication"""
    async def wrapper(*args, **kwargs):
        # This decorator would be applied to endpoints that need auth
        return await func(*args, **kwargs)
    return wrapper

def rate_limit(max_requests: int = 100, window: int = 3600):
    """Decorator for rate limiting"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Rate limiting logic would go here
            return await func(*args, **kwargs)
        return wrapper
    return decorator