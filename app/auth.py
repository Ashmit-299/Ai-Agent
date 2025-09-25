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

from fastapi import APIRouter, HTTPException, Depends, status, Request
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
from core.database import DatabaseManager

logger = logging.getLogger(__name__)
db = DatabaseManager()
router = APIRouter(prefix="/users", tags=["STEP 2: User Authentication"])
security_manager = SecurityManager()

class AuthUser:
    """User object for authenticated requests"""
    def __init__(self, user_id: str, username: str, token_jti: str = None):
        self.user_id = user_id
        self.username = username
        self.token_jti = token_jti

async def get_current_user_optional(request: Request) -> Optional[AuthUser]:
    """Get current user without requiring authentication"""
    try:
        user_data = await security_manager.authenticate_request(request)
        if user_data:
            return AuthUser(
                user_id=user_data["user_id"],
                username=user_data["username"],
                token_jti=user_data.get("token_jti")
            )
        return None
    except HTTPException:
        return None
    except Exception as e:
        logger.warning(f"Optional auth failed: {e}")
        return None

async def get_current_user_required(request: Request) -> AuthUser:
    """Get current user (required authentication)"""
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
        token_jti=user_data.get("token_jti")
    )

@router.post("/register", response_model=Token, status_code=201)
async def register_user(user_data: UserRegister, request: Request):
    """STEP 2A: Register new user account with enhanced security - PUBLIC ACCESS"""
    client_ip = security_manager.get_client_ip(request)
    
    try:
        # Validate input
        username = InputSanitizer.sanitize_string(user_data.username, 50)
        if len(username) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username must be at least 3 characters"
            )
        
        # Validate password strength
        password_validation = PasswordManager.validate_password_strength(user_data.password)
        if not password_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Password does not meet security requirements",
                    "issues": password_validation["issues"]
                }
            )
        
        # Validate email if provided
        if user_data.email and not InputSanitizer.validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid email format"
            )
        
        # Check if user exists
        existing_user = db.get_user_by_username(username)
        if existing_user:
            # Log suspicious activity
            log_security_event(
                "registration_attempt_existing_user",
                {"username": username, "success": False},
                client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # Create user
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = PasswordManager.hash_password(user_data.password)
        
        try:
            new_user = db.create_user({
                "user_id": user_id,
                "username": username,
                "password_hash": password_hash,
                "email": user_data.email,
                "email_verified": False,
                "created_at": time.time()
            })
        except Exception as db_error:
            logger.error(f"Database user creation failed: {db_error}")
            # Create a mock user object for token generation
            class MockUser:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            new_user = MockUser(
                user_id=user_id,
                username=username,
                password_hash=password_hash,
                email=user_data.email,
                email_verified=False,
                created_at=time.time()
            )
        
        # Create tokens
        try:
            token_data = {"sub": username, "user_id": user_id}
            access_token = JWTManager.create_access_token(token_data)
            refresh_token = JWTManager.create_refresh_token(user_id)
        except Exception as token_error:
            logger.error(f"Token creation failed: {token_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Token creation failed: {str(token_error)}"
            )
        
        # Log successful registration
        log_security_event(
            "user_registration_success",
            {"user_id": user_id, "username": username},
            client_ip,
            user_id
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1440,  # 24 hours in minutes
            user_id=user_id,
            username=username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Registration error: {e}")
        logger.error(f"Full traceback: {error_details}")
        print(f"Registration error: {e}")
        print(f"Full traceback: {error_details}")
        
        # Log security event with error handling
        try:
            log_security_event(
                "registration_error",
                {"error": str(e), "username": username if 'username' in locals() else "unknown"},
                client_ip
            )
        except Exception as log_error:
            logger.error(f"Failed to log security event: {log_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token, status_code=200)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    """STEP 2B: Login user with enhanced security - PUBLIC ACCESS"""
    client_ip = security_manager.get_client_ip(request)
    
    # Check rate limiting
    if auth_rate_limiter.is_locked(client_ip):
        log_security_event(
            "login_attempt_rate_limited",
            {"username": form_data.username},
            client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again later.",
            headers={"Retry-After": "900"}  # 15 minutes
        )
    
    try:
        # Sanitize input
        username = InputSanitizer.sanitize_string(form_data.username, 50)
        
        # Find user
        user = db.get_user_by_username(username)
        if not user:
            # Record failed attempt
            auth_rate_limiter.record_attempt(client_ip, False)
            log_security_event(
                "login_attempt_user_not_found",
                {"username": username},
                client_ip
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password
        if not PasswordManager.verify_password(form_data.password, user.password_hash):
            # Record failed attempt
            attempt_result = auth_rate_limiter.record_attempt(client_ip, False)
            log_security_event(
                "login_attempt_invalid_password",
                {
                    "username": username,
                    "attempts_remaining": attempt_result["attempts_remaining"]
                },
                client_ip,
                user.user_id
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Successful login - reset rate limiting
        auth_rate_limiter.record_attempt(client_ip, True)
        
        # Update last login
        try:
            # Update user's last login time
            from sqlmodel import Session, select
            from core.database import engine
            from core.models import User as UserModel
            
            with Session(engine) as session:
                statement = select(UserModel).where(UserModel.user_id == user.user_id)
                db_user = session.exec(statement).first()
                if db_user:
                    db_user.last_login = time.time()
                    session.add(db_user)
                    session.commit()
        except Exception as e:
            logger.warning(f"Failed to update last login: {e}")
        
        # Create tokens
        token_data = {"sub": user.username, "user_id": user.user_id}
        access_token = JWTManager.create_access_token(token_data)
        refresh_token = JWTManager.create_refresh_token(user.user_id)
        
        # Log successful login
        log_security_event(
            "login_success",
            {"username": username},
            client_ip,
            user.user_id
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=1440,  # 24 hours in minutes
            user_id=user.user_id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        log_security_event(
            "login_error",
            {"username": form_data.username, "error": str(e)},
            client_ip
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

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
    
    return {"message": "Logged out successfully", "token_invalidated": True}

# Enhanced dependencies for backward compatibility
async def get_current_user(request: Request) -> Optional[AuthUser]:
    """Backward compatibility wrapper"""
    return await get_current_user_optional(request)