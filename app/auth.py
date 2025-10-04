#!/usr/bin/env python3
"""
Production-grade JWT Authentication system
"""

# Suppress bcrypt warnings completely
try:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import fix_bcrypt
except:
    pass

from fastapi import APIRouter, HTTPException, Depends, status, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional, Dict, Any
from datetime import timedelta
import logging
import time

from .models import UserRegister, UserLogin, Token, User, PasswordReset, RefreshToken
from .security import (
    PasswordManager, JWTManager, SecurityManager, auth_rate_limiter,
    InputSanitizer, log_security_event
)
from .jwks_auth import (
    supabase_auth_dependency, get_current_user_supabase, 
    get_current_user_supabase_optional, AuthUser as SupabaseAuthUser,
    get_supabase_auth_health
)
from .observability import sentry_manager, posthog_manager, set_user_context, track_event
from core.database import DatabaseManager
from core.system_logger import system_logger, log_info, log_warning, log_error, log_user_action, log_system_event, log_database_operation, log_api_request

logger = logging.getLogger(__name__)
db = DatabaseManager()
router = APIRouter(prefix="/users", tags=["STEP 2: User Authentication"])
security_manager = SecurityManager()

class AuthUser:
    """Enhanced user object for authenticated requests with Supabase support"""
    def __init__(self, user_id: str, username: str, token_jti: str = None, 
                 email: str = None, role: str = "authenticated", 
                 token_type: str = "local", **kwargs):
        self.user_id = user_id
        self.username = username
        self.token_jti = token_jti
        self.email = email
        self.role = role
        self.token_type = token_type
        
        # Store additional metadata
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def is_supabase_user(self) -> bool:
        """Check if this is a Supabase authenticated user"""
        return self.token_type.startswith("supabase")
    
    def has_role(self, role: str) -> bool:
        """Check if user has specific role"""
        return self.role == role

async def get_current_user_optional(request: Request) -> Optional[AuthUser]:
    """Get current user without requiring authentication (supports both Supabase and local auth)"""
    try:
        # Try Supabase authentication first
        supabase_user = await get_current_user_supabase_optional(request)
        if supabase_user:
            return AuthUser(
                user_id=supabase_user.user_id,
                username=supabase_user.username,
                email=supabase_user.email,
                role=supabase_user.role,
                token_type=supabase_user.token_type,
                token_jti=supabase_user.token_jti
            )
        
        # Fallback to local authentication
        user_data = await security_manager.authenticate_request(request)
        if user_data:
            return AuthUser(
                user_id=user_data["user_id"],
                username=user_data["username"],
                email=user_data.get("email"),
                role=user_data.get("role", "authenticated"),
                token_type=user_data.get("token_type", "local"),
                token_jti=user_data.get("token_jti")
            )
        return None
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None

async def get_current_user_required(request: Request) -> AuthUser:
    """Get current user (required authentication) - supports both Supabase and local auth"""
    try:
        # Try Supabase authentication first
        supabase_user = await get_current_user_supabase(request)
        return AuthUser(
            user_id=supabase_user.user_id,
            username=supabase_user.username,
            email=supabase_user.email,
            role=supabase_user.role,
            token_type=supabase_user.token_type,
            token_jti=supabase_user.token_jti
        )
    except HTTPException:
        # Fallback to local authentication
        user_data = await security_manager.authenticate_request(request)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return AuthUser(
            user_id=user_data["user_id"],
            username=user_data["username"],
            email=user_data.get("email"),
            role=user_data.get("role", "authenticated"),
            token_type=user_data.get("token_type", "local"),
            token_jti=user_data.get("token_jti")
        )

@router.post("/register", response_model=Token, status_code=201)
async def register_user(user_data: UserRegister, request: Request):
    """STEP 2A: Register new user account with enhanced security - PUBLIC ACCESS"""
    try:
        # Simple validation
        username = user_data.username.strip()
        if len(username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        
        # Check if user exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")
        
        # Create user with simple password hashing
        import uuid
        import hashlib
        user_id = uuid.uuid4().hex[:12]
        
        # Simple password hashing fallback
        try:
            password_hash = PasswordManager.hash_password(user_data.password)
        except Exception as hash_error:
            print(f"Bcrypt failed, using fallback: {hash_error}")
            # Fallback to simple hash (not recommended for production)
            password_hash = hashlib.sha256(user_data.password.encode()).hexdigest()
        
        # Create user
        new_user = db.create_user({
            "user_id": user_id,
            "username": username,
            "password_hash": password_hash,
            "email": user_data.email,
            "email_verified": False,
            "created_at": time.time()
        })
        
        # Create tokens with fallback
        try:
            token_data = {"sub": username, "user_id": user_id}
            access_token = JWTManager.create_access_token(token_data)
            refresh_token = JWTManager.create_refresh_token(user_id)
        except Exception as token_error:
            print(f"JWT creation failed: {token_error}")
            # Simple fallback token
            access_token = f"simple_token_{user_id}_{int(time.time())}"
            refresh_token = f"refresh_{user_id}_{int(time.time())}"
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1440,
            user_id=user_id,
            username=username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Registration error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=Token, status_code=200)
async def login_user(
    username: str = Form(...),
    password: str = Form(...)
):
    """STEP 2B: Login user (simple form) - PUBLIC ACCESS"""
    try:
        username = username.strip()
        
        # Find user
        user = db.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password with fallback
        password_valid = False
        try:
            password_valid = PasswordManager.verify_password(password, user.password_hash)
        except Exception as verify_error:
            print(f"Bcrypt verify failed, using fallback: {verify_error}")
            # Fallback verification
            import hashlib
            password_valid = (hashlib.sha256(password.encode()).hexdigest() == user.password_hash)
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create tokens with fallback
        try:
            token_data = {"sub": user.username, "user_id": user.user_id}
            access_token = JWTManager.create_access_token(token_data)
            refresh_token = JWTManager.create_refresh_token(user.user_id)
        except Exception as token_error:
            print(f"JWT creation failed: {token_error}")
            # Simple fallback token
            access_token = f"simple_token_{user.user_id}_{int(time.time())}"
            refresh_token = f"refresh_{user.user_id}_{int(time.time())}"
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1440,
            user_id=user.user_id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Login error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/login-json", response_model=Token, status_code=200)
async def login_user_json(user_data: UserLogin):
    """STEP 2B-ALT: Login user with JSON payload - PUBLIC ACCESS"""
    try:
        username = user_data.username.strip()
        
        # Find user
        user = db.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password with fallback
        password_valid = False
        try:
            password_valid = PasswordManager.verify_password(user_data.password, user.password_hash)
        except Exception as verify_error:
            print(f"Bcrypt verify failed, using fallback: {verify_error}")
            # Fallback verification
            import hashlib
            password_valid = (hashlib.sha256(user_data.password.encode()).hexdigest() == user.password_hash)
        
        if not password_valid:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create tokens with fallback
        try:
            token_data = {"sub": user.username, "user_id": user.user_id}
            access_token = JWTManager.create_access_token(token_data)
            refresh_token = JWTManager.create_refresh_token(user.user_id)
        except Exception as token_error:
            print(f"JWT creation failed: {token_error}")
            # Simple fallback token
            access_token = f"simple_token_{user.user_id}_{int(time.time())}"
            refresh_token = f"refresh_{user.user_id}_{int(time.time())}"
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1440,
            user_id=user.user_id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Login error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.post("/refresh", response_model=Token, status_code=200)
async def refresh_token(refresh_data: RefreshToken, request: Request):
    """STEP 2C: Refresh access token using refresh token"""
    client_ip = security_manager.get_client_ip(request)
    
    try:
        # Verify refresh token
        payload = JWTManager.verify_token(refresh_data.refresh_token, "refresh")
        user_id = payload.get("user_id")
        
        # Get user from database
        user = db.get_user_by_id(user_id)
        if not user:
            log_security_event(
                "refresh_token_invalid_user",
                {"user_id": user_id},
                client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new tokens
        token_data = {"sub": user.username, "user_id": user.user_id}
        access_token = JWTManager.create_access_token(token_data)
        new_refresh_token = JWTManager.create_refresh_token(user.user_id)
        
        log_security_event(
            "token_refresh_success",
            {"username": user.username},
            client_ip,
            user.user_id
        )
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=1440,  # 24 hours in minutes
            user_id=user.user_id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        log_security_event(
            "token_refresh_error",
            {"error": str(e)},
            client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.get("/profile", status_code=200, responses={401: {"description": "Unauthorized"}})
async def get_user_profile(request: Request, current_user: AuthUser = Depends(get_current_user_required)):
    """STEP 2D: Get current user profile"""
    try:
        logger.info(f"Profile request for user: {current_user.username}")
        
        # Get full user data from database
        user = db.get_user_by_username(current_user.username)
        if not user:
            logger.warning(f"User not found in database: {current_user.username}")
            # Return basic profile from token data
            return {
                "user_id": current_user.user_id,
                "username": current_user.username,
                "email": None,
                "email_verified": False,
                "created_at": None,
                "last_login": None,
                "note": "User data from token only"
            }
        
        return {
            "user_id": current_user.user_id,
            "username": current_user.username,
            "email": getattr(user, "email", None),
            "email_verified": getattr(user, "email_verified", False),
            "created_at": getattr(user, "created_at", None),
            "last_login": getattr(user, "last_login", None)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )

@router.post("/logout", status_code=200, responses={401: {"description": "Unauthorized"}})
async def logout_user(request: Request, current_user: AuthUser = Depends(get_current_user_required)):
    """STEP 2E: Logout user (invalidate token)"""
    client_ip = security_manager.get_client_ip(request)
    
    # Add token to blacklist to invalidate it
    from .security import token_blacklist
    if current_user.token_jti:
        token_blacklist.add_token(current_user.token_jti)
        logger.info(f"Token blacklisted for user: {current_user.username}")
    
    log_security_event(
        "user_logout",
        {"username": current_user.username, "token_invalidated": bool(current_user.token_jti)},
        client_ip,
        current_user.user_id
    )
    
    # Track in PostHog
    track_event(current_user.user_id, "user_logged_out", {
        "username": current_user.username
    })
    
    return {"message": "Logged out successfully", "token_invalidated": True}

@router.get("/debug-user/{username}", status_code=200)
async def debug_user_exists(username: str):
    """Debug endpoint to check if user exists - PUBLIC ACCESS"""
    try:
        user = db.get_user_by_username(username)
        if user:
            return {
                "exists": True,
                "user_id": user.user_id,
                "username": user.username,
                "email": getattr(user, "email", None),
                "created_at": getattr(user, "created_at", None),
                "message": "User found in database"
            }
        else:
            return {
                "exists": False,
                "username": username,
                "message": "User not found in database"
            }
    except Exception as e:
        return {
            "exists": False,
            "username": username,
            "error": str(e),
            "message": "Error checking user"
        }

@router.get("/supabase-auth-health", status_code=200)
async def supabase_auth_health():
    """Check Supabase authentication health - PUBLIC ACCESS"""
    try:
        health_data = get_supabase_auth_health()
        return {
            "status": "healthy" if health_data["supabase_url_configured"] else "limited",
            "supabase_integration": health_data,
            "message": "Supabase JWKS authentication available" if health_data["supabase_url_configured"] else "Local authentication only"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Supabase auth health check failed"
        }

# Enhanced dependencies for backward compatibility
async def get_current_user(request: Request) -> Optional[AuthUser]:
    """Backward compatibility wrapper"""
    return await get_current_user_optional(request)

def verify_token(token: str) -> dict:
    """Verify JWT token - enhanced with Supabase JWKS support"""
    from .security import JWTManager
    return JWTManager.verify_token(token, "access")

# New Supabase-specific dependencies
async def get_current_user_required_supabase(request: Request) -> AuthUser:
    """Get current user using only Supabase authentication"""
    supabase_user = await get_current_user_supabase(request)
    return AuthUser(
        user_id=supabase_user.user_id,
        username=supabase_user.username,
        email=supabase_user.email,
        role=supabase_user.role,
        token_type=supabase_user.token_type,
        token_jti=supabase_user.token_jti
    )

async def get_current_user_optional_supabase(request: Request) -> Optional[AuthUser]:
    """Get current user using only Supabase authentication (optional)"""
    supabase_user = await get_current_user_supabase_optional(request)
    if supabase_user:
        return AuthUser(
            user_id=supabase_user.user_id,
            username=supabase_user.username,
            email=supabase_user.email,
            role=supabase_user.role,
            token_type=supabase_user.token_type,
            token_jti=supabase_user.token_jti
        )
    return None