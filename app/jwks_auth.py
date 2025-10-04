#!/usr/bin/env python3
"""
Supabase JWKS Authentication Module
Enhanced JWT validation with Supabase JWKS support
"""

import os
import httpx
import logging
from jose import jwt, JWTError
from fastapi import Request, HTTPException, status
from functools import lru_cache
from typing import Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
JWT_AUD = os.getenv("JWT_AUD", "authenticated")
ALGORITHMS = ["RS256", "HS256"]

# Construct JWKS URL
JWKS_URL = f"{SUPABASE_URL}/.well-known/jwks.json" if SUPABASE_URL else None

class SupabaseJWKSAuth:
    """Supabase JWKS Authentication Handler"""
    
    def __init__(self):
        self.jwks_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 3600  # 1 hour cache
    
    @lru_cache(maxsize=1)
    def get_jwks(self) -> Optional[Dict]:
        """Fetch and cache Supabase JWKS"""
        if not JWKS_URL:
            logger.warning("SUPABASE_URL not configured, JWKS unavailable")
            return None
        
        try:
            # Check cache validity
            current_time = time.time()
            if (self.jwks_cache and 
                current_time - self.cache_timestamp < self.cache_ttl):
                return self.jwks_cache
            
            # Fetch fresh JWKS
            logger.info(f"Fetching JWKS from: {JWKS_URL}")
            response = httpx.get(JWKS_URL, timeout=10.0)
            response.raise_for_status()
            
            self.jwks_cache = response.json()
            self.cache_timestamp = current_time
            
            logger.info("JWKS fetched and cached successfully")
            return self.jwks_cache
            
        except httpx.TimeoutException:
            logger.error("JWKS fetch timeout")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"JWKS fetch HTTP error: {e.response.status_code}")
            return None
        except Exception as e:
            logger.error(f"JWKS fetch failed: {e}")
            return None
    
    def verify_supabase_token(self, token: str) -> Dict[str, Any]:
        """Verify Supabase JWT token using JWKS"""
        try:
            # Method 1: Try JWKS verification (for RS256 tokens)
            jwks = self.get_jwks()
            if jwks:
                try:
                    payload = jwt.decode(
                        token,
                        jwks,
                        algorithms=["RS256"],
                        audience=JWT_AUD,
                        issuer=f"{SUPABASE_URL}/auth/v1" if SUPABASE_URL else None,
                    )
                    logger.info("Token verified using JWKS (RS256)")
                    return self._normalize_supabase_payload(payload)
                except JWTError as e:
                    logger.debug(f"JWKS verification failed: {e}")
            
            # Method 2: Try direct secret verification (for HS256 tokens)
            if SUPABASE_JWT_SECRET:
                try:
                    payload = jwt.decode(
                        token,
                        SUPABASE_JWT_SECRET,
                        algorithms=["HS256"],
                        audience=JWT_AUD,
                        issuer=f"{SUPABASE_URL}/auth/v1" if SUPABASE_URL else None,
                    )
                    logger.info("Token verified using JWT secret (HS256)")
                    return self._normalize_supabase_payload(payload)
                except JWTError as e:
                    logger.debug(f"JWT secret verification failed: {e}")
            
            # If both methods fail
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired Supabase token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Supabase token verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token verification failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def _normalize_supabase_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Supabase JWT payload to our format"""
        return {
            "user_id": payload.get("sub"),
            "username": payload.get("email", payload.get("sub")),
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "aud": payload.get("aud"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat"),
            "iss": payload.get("iss"),
            "token_type": "supabase",
            "app_metadata": payload.get("app_metadata", {}),
            "user_metadata": payload.get("user_metadata", {}),
            "raw_payload": payload
        }

# Global instance
supabase_jwks_auth = SupabaseJWKSAuth()

async def supabase_auth_dependency(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency for Supabase JWT authentication
    Extracts and validates Supabase JWT tokens
    """
    # Extract Authorization header
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract token
    token = auth_header[len("Bearer "):]
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify token
    return supabase_jwks_auth.verify_supabase_token(token)

def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Standalone function to verify Supabase tokens
    Can be used outside of FastAPI dependencies
    """
    return supabase_jwks_auth.verify_supabase_token(token)

class AuthUser:
    """Enhanced AuthUser class for Supabase integration"""
    
    def __init__(self, user_id: str, username: str, token_jti: str = None, 
                 email: str = None, role: str = "authenticated", 
                 token_type: str = "local", **kwargs):
        self.user_id = user_id
        self.username = username
        self.token_jti = token_jti
        self.email = email
        self.role = role
        self.token_type = token_type
        
        # Store additional Supabase metadata
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def is_supabase_user(self) -> bool:
        """Check if this is a Supabase authenticated user"""
        return self.token_type == "supabase"
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return self.role == role
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "token_type": self.token_type,
            "token_jti": self.token_jti
        }

async def get_current_user_supabase(request: Request) -> AuthUser:
    """
    Get current user using Supabase JWKS authentication
    This is the enhanced version that supports Supabase tokens
    """
    try:
        # Try Supabase authentication first
        payload = await supabase_auth_dependency(request)
        
        return AuthUser(
            user_id=payload["user_id"],
            username=payload["username"],
            email=payload.get("email"),
            role=payload.get("role", "authenticated"),
            token_type="supabase",
            app_metadata=payload.get("app_metadata", {}),
            user_metadata=payload.get("user_metadata", {}),
            raw_payload=payload.get("raw_payload", {})
        )
        
    except HTTPException as e:
        # If Supabase auth fails, fall back to local auth
        logger.debug(f"Supabase auth failed, trying local auth: {e.detail}")
        
        # Import local auth to avoid circular imports
        from .security import security_manager
        
        try:
            user_data = await security_manager.authenticate_request(request)
            if user_data:
                return AuthUser(
                    user_id=user_data["user_id"],
                    username=user_data["username"],
                    token_jti=user_data.get("token_jti"),
                    token_type="local"
                )
        except Exception as local_error:
            logger.debug(f"Local auth also failed: {local_error}")
        
        # Re-raise the original Supabase error
        raise e

async def get_current_user_supabase_optional(request: Request) -> Optional[AuthUser]:
    """
    Optional Supabase authentication - returns None if not authenticated
    """
    try:
        return await get_current_user_supabase(request)
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional Supabase auth error: {e}")
        return None

# Health check function
def get_supabase_auth_health() -> Dict[str, Any]:
    """Get health status of Supabase authentication"""
    return {
        "supabase_url_configured": bool(SUPABASE_URL),
        "supabase_jwt_secret_configured": bool(SUPABASE_JWT_SECRET),
        "jwks_url": JWKS_URL,
        "jwks_cache_valid": bool(supabase_jwks_auth.jwks_cache),
        "cache_age_seconds": time.time() - supabase_jwks_auth.cache_timestamp if supabase_jwks_auth.cache_timestamp else None,
        "supported_algorithms": ALGORITHMS,
        "audience": JWT_AUD
    }