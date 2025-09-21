#!/usr/bin/env python3
"""
JWT Authentication system with user management
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from .models import UserRegister, UserLogin, Token, User
from datetime import datetime, timedelta
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# JWT and password hashing imports
try:
    from jose import jwt, JWTError
    from passlib.context import CryptContext
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    import hashlib
    import hmac

from core.database import DatabaseManager
db = DatabaseManager()

router = APIRouter(prefix="/users", tags=["STEP 2: User Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SECRET_KEY = os.getenv("JWT_SECRET", "change_this_secret_key_in_production")
PUB_KEY = os.getenv("SUPABASE_PUBLIC_KEY")
ALG = "RS256"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days for alpha

# Password hashing
if JWT_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None

# Models imported from .models module

def hash_password(password: str) -> str:
    """Hash password using bcrypt or fallback"""
    if pwd_context:
        return pwd_context.hash(password)
    else:
        # Simple fallback hashing
        import hashlib
        return hashlib.pbkdf2_hmac('sha256', password.encode(), b'salt', 100000).hex()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt or fallback"""
    if pwd_context:
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Simple fallback verification
        import hashlib
        return hashed_password == hashlib.pbkdf2_hmac('sha256', plain_password.encode(), b'salt', 100000).hex()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    if JWT_AVAILABLE:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        # Simple fallback token (not secure for production)
        import json
        import base64
        token_data = json.dumps(to_encode, default=str)
        return base64.b64encode(token_data.encode()).decode()

def verify_token(token: str) -> dict:
    """Verify JWT token"""
    if JWT_AVAILABLE:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    else:
        # Simple fallback verification
        try:
            import json
            import base64
            token_data = base64.b64decode(token.encode()).decode()
            return json.loads(token_data)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")



async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current authenticated user"""
    try:
        payload = verify_token(token)
        user_id = payload.get("user_id")
        username = payload.get("sub")
        
        if not user_id or not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        # Return user object with required fields
        class AuthUser:
            def __init__(self, user_id: str, username: str):
                self.user_id = user_id
                self.username = username
        
        return AuthUser(user_id, username)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user_required(current_user = Depends(get_current_user)):
    """Get current user (required authentication)"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return current_user

@router.post("/register", response_model=Token, status_code=201)
async def register_user(user_data: UserRegister):
    """STEP 2A: Register new user account"""
    try:
        # Validate input
        if len(user_data.username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
        if len(user_data.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
        
        # Check if user exists
        existing_user = db.get_user_by_username(user_data.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create user
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = hash_password(user_data.password)
        
        new_user = db.create_user({
            "user_id": user_id,
            "username": user_data.username,
            "password_hash": password_hash,
            "email": user_data.email
        })
        
        # Create token
        token_data = {"sub": user_data.username, "user_id": user_id}
        access_token = create_access_token(token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            username=user_data.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token, status_code=200)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """STEP 2B: Login user and get JWT token (OAuth2 compatible)"""
    try:
        # Find user
        user = db.get_user_by_username(form_data.username)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create token
        token_data = {"sub": user.username, "user_id": user.user_id}
        access_token = create_access_token(token_data)
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user_id=user.user_id,
            username=user.username
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile", status_code=200)
async def get_user_profile(current_user = Depends(get_current_user_required)):
    """STEP 2C: Get current user profile (requires authentication)"""
    # Get full user data from database
    user = db.get_user_by_username(current_user.username)
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": user.email if user else None,
        "created_at": user.created_at if user else None
    }

@router.get("/me", response_model=User, status_code=200)
async def get_current_user_info(current_user = Depends(get_current_user_required)):
    """STEP 2D: Get current user info - alternative endpoint (requires authentication)"""
    # Get full user data from database
    user = db.get_user_by_username(current_user.username)
    return User(
        user_id=current_user.user_id,
        username=current_user.username,
        email=user.email if user else None
    )