#!/usr/bin/env python3
"""
Supabase JWT Authentication with JWKS validation
"""
import os
import jwt
import requests
import time
from typing import Optional, Dict, Any
from functools import lru_cache
from fastapi import HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

logger = logging.getLogger(__name__)

class SupabaseAuth:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "")
        self.supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "")
        self.jwks_cache = {}
        self.jwks_cache_expiry = 0
        self.cache_duration = 3600  # 1 hour
        
        if not self.supabase_url:
            logger.warning("SUPABASE_URL not set, JWT validation will use fallback")
        if not self.supabase_jwt_secret:
            logger.warning("SUPABASE_JWT_SECRET not set, JWT validation will use fallback")

    @lru_cache(maxsize=1)
    def get_jwks_uri(self) -> str:
        """Get JWKS URI from Supabase"""
        if not self.supabase_url:
            return ""
        return f"{self.supabase_url}/auth/v1/.well-known/jwks.json"

    def fetch_jwks(self) -> Dict[str, Any]:
        """Fetch JWKS from Supabase with caching"""
        current_time = time.time()
        
        # Return cached JWKS if still valid
        if self.jwks_cache and current_time < self.jwks_cache_expiry:
            return self.jwks_cache
        
        try:
            jwks_uri = self.get_jwks_uri()
            if not jwks_uri:
                return {}
                
            response = requests.get(jwks_uri, timeout=10)
            response.raise_for_status()
            
            jwks_data = response.json()
            
            # Cache the JWKS
            self.jwks_cache = jwks_data
            self.jwks_cache_expiry = current_time + self.cache_duration
            
            logger.info("JWKS fetched and cached successfully")
            return jwks_data
            
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {e}")
            return {}

    def get_public_key(self, kid: str) -> Optional[str]:
        """Get public key for given key ID"""
        jwks = self.fetch_jwks()
        
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        return None

    def validate_supabase_token(self, token: str) -> Dict[str, Any]:
        """Validate Supabase JWT token using JWKS"""
        try:
            # Decode header to get key ID
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            
            if not kid:
                raise HTTPException(status_code=401, detail="Token missing key ID")
            
            # Get public key
            public_key = self.get_public_key(kid)
            if not public_key:
                raise HTTPException(status_code=401, detail="Unable to verify token signature")
            
            # Verify and decode token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="authenticated",
                issuer=f"{self.supabase_url}/auth/v1"
            )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            raise HTTPException(status_code=401, detail="Token validation failed")

    def fallback_validation(self, token: str) -> Dict[str, Any]:
        """Fallback JWT validation using secret"""
        try:
            if self.supabase_jwt_secret:
                payload = jwt.decode(
                    token, 
                    self.supabase_jwt_secret, 
                    algorithms=["HS256"]
                )
                return payload
            else:
                # Simple token validation for development
                if token.startswith("simple_token_"):
                    parts = token.split("_")
                    if len(parts) >= 3:
                        return {
                            "sub": parts[2],
                            "user_id": parts[2],
                            "aud": "authenticated",
                            "role": "authenticated"
                        }
                raise HTTPException(status_code=401, detail="Invalid token format")
                
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def validate_token(self, token: str) -> Dict[str, Any]:
        """Main token validation method with fallback"""
        # Try Supabase JWKS validation first
        if self.supabase_url and self.supabase_jwt_secret:
            try:
                return self.validate_supabase_token(token)
            except HTTPException as e:
                logger.warning(f"JWKS validation failed: {e.detail}, trying fallback")
        
        # Fallback to secret-based validation
        return self.fallback_validation(token)

# Global instance
supabase_auth = SupabaseAuth()

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user_supabase(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user using Supabase JWT validation"""
    
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = supabase_auth.validate_token(token)
        
        # Extract user information
        user_data = {
            "user_id": payload.get("sub", payload.get("user_id")),
            "email": payload.get("email"),
            "role": payload.get("role", "authenticated"),
            "aud": payload.get("aud"),
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        
        return user_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

async def require_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """Require authentication - raises 401 if no valid token"""
    
    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_data = await get_current_user_supabase(request, credentials)
    if not user_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user_data

# Backward compatibility wrapper
class AuthUser:
    def __init__(self, user_data: Dict[str, Any]):
        self.user_id = user_data.get("user_id")
        self.email = user_data.get("email")
        self.role = user_data.get("role", "authenticated")
        self.token_data = user_data

async def get_current_user_required_supabase(request: Request) -> AuthUser:
    """Get current authenticated user - Supabase version"""
    user_data = await require_auth(request)
    return AuthUser(user_data)

async def get_current_user_optional_supabase(request: Request) -> Optional[AuthUser]:
    """Get current user if authenticated - Supabase version"""
    try:
        user_data = await get_current_user_supabase(request)
        return AuthUser(user_data) if user_data else None
    except HTTPException:
        return None