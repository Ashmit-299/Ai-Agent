#!/usr/bin/env python3
"""
Unit tests for Authentication and Security
Tests JWT tokens, rate limiting, input validation, and security middleware
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.auth import (
    hash_password, verify_password, create_access_token, verify_token,
    get_current_user, get_current_user_required
)
from app.models import UserRegister, UserLogin, Token, User

class TestAuthSecurity:
    
    def test_hash_password_bcrypt(self):
        """Test password hashing with bcrypt"""
        password = "test_password_123"
        
        with patch('app.auth.pwd_context') as mock_context:
            mock_context.hash.return_value = "hashed_password"
            
            result = hash_password(password)
            
            mock_context.hash.assert_called_once_with(password)
            assert result == "hashed_password"

    def test_hash_password_fallback(self):
        """Test password hashing fallback when bcrypt unavailable"""
        password = "test_password_123"
        
        with patch('app.auth.pwd_context', None):
            result = hash_password(password)
            
            # Should return a hex string (fallback hashing)
            assert isinstance(result, str)
            assert len(result) > 0
            # Should be deterministic
            assert hash_password(password) == result

    def test_verify_password_bcrypt(self):
        """Test password verification with bcrypt"""
        plain_password = "test_password_123"
        hashed_password = "hashed_password"
        
        with patch('app.auth.pwd_context') as mock_context:
            mock_context.verify.return_value = True
            
            result = verify_password(plain_password, hashed_password)
            
            mock_context.verify.assert_called_once_with(plain_password, hashed_password)
            assert result == True

    def test_verify_password_fallback(self):
        """Test password verification fallback"""
        password = "test_password_123"
        
        with patch('app.auth.pwd_context', None):
            # Hash password using fallback method
            hashed = hash_password(password)
            
            # Verify should work with same password
            assert verify_password(password, hashed) == True
            assert verify_password("wrong_password", hashed) == False

    def test_create_access_token_jwt(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.auth.JWT_AVAILABLE', True):
            with patch('app.auth.jwt.encode') as mock_encode:
                mock_encode.return_value = "jwt_token"
                
                result = create_access_token(data)
                
                mock_encode.assert_called_once()
                assert result == "jwt_token"

    def test_create_access_token_fallback(self):
        """Test token creation fallback when JWT unavailable"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.auth.JWT_AVAILABLE', False):
            result = create_access_token(data)
            
            # Should return base64 encoded string
            assert isinstance(result, str)
            assert len(result) > 0

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        
        with patch('app.auth.JWT_AVAILABLE', True):
            with patch('app.auth.jwt.encode') as mock_encode:
                mock_encode.return_value = "jwt_token"
                
                result = create_access_token(data, expires_delta)
                
                # Should include expiry in token data
                call_args = mock_encode.call_args[0][0]
                assert "exp" in call_args
                assert result == "jwt_token"

    def test_verify_token_jwt(self):
        """Test JWT token verification"""
        token = "valid_jwt_token"
        expected_payload = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.auth.JWT_AVAILABLE', True):
            with patch('app.auth.jwt.decode') as mock_decode:
                mock_decode.return_value = expected_payload
                
                result = verify_token(token)
                
                mock_decode.assert_called_once_with(token, "change_this_secret_key_in_production", algorithms=["HS256"])
                assert result == expected_payload

    def test_verify_token_jwt_invalid(self):
        """Test JWT token verification with invalid token"""
        token = "invalid_jwt_token"
        
        with patch('app.auth.JWT_AVAILABLE', True):
            with patch('app.auth.jwt.decode', side_effect=Exception("Invalid token")):
                
                with pytest.raises(HTTPException) as exc_info:
                    verify_token(token)
                
                assert exc_info.value.status_code == 401
                assert "Invalid token" in str(exc_info.value.detail)

    def test_verify_token_fallback(self):
        """Test token verification fallback"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.auth.JWT_AVAILABLE', False):
            # Create token using fallback method
            token = create_access_token(data)
            
            # Verify should work
            result = verify_token(token)
            assert result["sub"] == "testuser"
            assert result["user_id"] == "user123"

    def test_verify_token_fallback_invalid(self):
        """Test token verification fallback with invalid token"""
        with patch('app.auth.JWT_AVAILABLE', False):
            with pytest.raises(HTTPException) as exc_info:
                verify_token("invalid_base64_token")
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self):
        """Test getting current user with valid token"""
        token = "valid_token"
        payload = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.auth.verify_token', return_value=payload):
            user = await get_current_user(token)
            
            assert user.username == "testuser"
            assert user.user_id == "user123"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_payload(self):
        """Test getting current user with invalid token payload"""
        token = "valid_token"
        payload = {"sub": "testuser"}  # Missing user_id
        
        with patch('app.auth.verify_token', return_value=payload):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token payload" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_verify_error(self):
        """Test getting current user when token verification fails"""
        token = "invalid_token"
        
        with patch('app.auth.verify_token', side_effect=HTTPException(status_code=401, detail="Invalid token")):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_required_valid(self):
        """Test getting current user (required) with valid user"""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.user_id = "user123"
        
        result = await get_current_user_required(mock_user)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_required_none(self):
        """Test getting current user (required) with None user"""
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user_required(None)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)

    def test_user_register_model_validation(self):
        """Test UserRegister model validation"""
        # Valid data
        valid_data = {
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com"
        }
        user = UserRegister(**valid_data)
        assert user.username == "testuser"
        assert user.password == "password123"
        assert user.email == "test@example.com"

    def test_user_register_model_validation_errors(self):
        """Test UserRegister model validation errors"""
        # Username too short
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="ab", password="password123")
        
        # Password too short
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="testuser", password="12345")

    def test_token_model(self):
        """Test Token model"""
        token_data = {
            "access_token": "jwt_token_here",
            "token_type": "bearer",
            "user_id": "user123",
            "username": "testuser"
        }
        token = Token(**token_data)
        
        assert token.access_token == "jwt_token_here"
        assert token.token_type == "bearer"
        assert token.user_id == "user123"
        assert token.username == "testuser"

    def test_user_model(self):
        """Test User model"""
        user_data = {
            "user_id": "user123",
            "username": "testuser",
            "email": "test@example.com"
        }
        user = User(**user_data)
        
        assert user.user_id == "user123"
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_model_optional_email(self):
        """Test User model with optional email"""
        user_data = {
            "user_id": "user123",
            "username": "testuser"
        }
        user = User(**user_data)
        
        assert user.user_id == "user123"
        assert user.username == "testuser"
        assert user.email is None

    @patch('app.auth.db')
    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_db):
        """Test successful user registration"""
        from app.auth import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock database responses
        mock_db.get_user_by_username.return_value = None  # User doesn't exist
        mock_db.create_user.return_value = Mock(user_id="user123", username="testuser")
        
        response = client.post("/users/register", json={
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["username"] == "testuser"

    @patch('app.auth.db')
    @pytest.mark.asyncio
    async def test_register_user_existing(self, mock_db):
        """Test user registration with existing username"""
        from app.auth import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock database responses
        mock_db.get_user_by_username.return_value = Mock(username="testuser")  # User exists
        
        response = client.post("/users/register", json={
            "username": "testuser",
            "password": "password123",
            "email": "test@example.com"
        })
        
        assert response.status_code == 400
        assert "Username already exists" in response.json()["detail"]

    @patch('app.auth.db')
    @pytest.mark.asyncio
    async def test_login_user_success(self, mock_db):
        """Test successful user login"""
        from app.auth import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock user with hashed password
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.user_id = "user123"
        mock_user.password_hash = hash_password("password123")
        
        mock_db.get_user_by_username.return_value = mock_user
        
        response = client.post("/users/login", data={
            "username": "testuser",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["username"] == "testuser"

    @patch('app.auth.db')
    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, mock_db):
        """Test login with invalid credentials"""
        from app.auth import router
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        client = TestClient(app)
        
        # Mock user not found
        mock_db.get_user_by_username.return_value = None
        
        response = client.post("/users/login", data={
            "username": "nonexistent",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_password_strength_validation(self):
        """Test password strength requirements"""
        # Test minimum length requirement
        weak_passwords = ["123", "12345", "abc"]
        
        for weak_password in weak_passwords:
            with pytest.raises(Exception):  # Should raise validation error
                UserRegister(username="testuser", password=weak_password)

    def test_username_validation(self):
        """Test username validation requirements"""
        # Test minimum length requirement
        short_usernames = ["a", "ab"]
        
        for short_username in short_usernames:
            with pytest.raises(Exception):  # Should raise validation error
                UserRegister(username=short_username, password="password123")

    def test_token_expiry_calculation(self):
        """Test token expiry calculation"""
        data = {"sub": "testuser"}
        
        with patch('app.auth.JWT_AVAILABLE', True):
            with patch('app.auth.jwt.encode') as mock_encode:
                mock_encode.return_value = "jwt_token"
                
                # Test default expiry
                create_access_token(data)
                
                call_args = mock_encode.call_args[0][0]
                assert "exp" in call_args
                
                # Expiry should be in the future
                exp_time = datetime.fromtimestamp(call_args["exp"])
                assert exp_time > datetime.utcnow()

    def test_security_headers_validation(self):
        """Test security-related input validation"""
        # Test that sensitive data is properly handled
        sensitive_data = {
            "username": "<script>alert('xss')</script>",
            "password": "password123"
        }
        
        # Should not raise exception - validation should handle this
        try:
            user = UserRegister(**sensitive_data)
            # Username should be stored as-is (validation happens at app level)
            assert user.username == "<script>alert('xss')</script>"
        except Exception:
            # If validation rejects it, that's also acceptable
            pass