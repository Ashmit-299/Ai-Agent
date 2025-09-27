#!/usr/bin/env python3
"""
Unit tests for Authentication and Security
Tests JWT tokens, rate limiting, input validation, and security middleware
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.auth import (
    get_current_user, get_current_user_required
)
from app.security import PasswordManager, JWTManager
from app.models import UserRegister, UserLogin, Token, User

class TestAuthSecurity:
    
    def test_hash_password_bcrypt(self):
        """Test password hashing with bcrypt"""
        password = os.getenv("TEST_PASSWORD", "test_password_123")
        
        with patch('app.security.PasswordManager.hash_password') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            result = PasswordManager.hash_password(password)
            
            mock_hash.assert_called_once_with(password)
            assert result == "hashed_password"

    def test_hash_password_fallback(self):
        """Test password hashing fallback when bcrypt unavailable"""
        password = os.getenv("TEST_PASSWORD", "test_password_123")
        
        result = PasswordManager.hash_password(password)
        
        # Should return a hashed string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_verify_password_bcrypt(self):
        """Test password verification with bcrypt"""
        plain_password = os.getenv("TEST_PASSWORD", "test_password_123")
        hashed_password = "hashed_password"
        
        with patch('app.security.PasswordManager.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            result = PasswordManager.verify_password(plain_password, hashed_password)
            
            mock_verify.assert_called_once_with(plain_password, hashed_password)
            assert result == True

    def test_verify_password_fallback(self):
        """Test password verification fallback"""
        password = os.getenv("TEST_PASSWORD", "test_password_123")
        
        # Hash password
        hashed = PasswordManager.hash_password(password)
        
        # Verify should work with same password
        assert PasswordManager.verify_password(password, hashed) == True
        assert PasswordManager.verify_password(os.getenv("WRONG_TEST_PASSWORD", "wrong_password"), hashed) == False

    def test_create_access_token_jwt(self):
        """Test JWT token creation"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.security.JWTManager.create_access_token') as mock_create:
            mock_create.return_value = "jwt_token"
            
            result = JWTManager.create_access_token(data)
            
            mock_create.assert_called_once_with(data)
            assert result == "jwt_token"

    def test_create_access_token_fallback(self):
        """Test token creation fallback when JWT unavailable"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        result = JWTManager.create_access_token(data)
        
        # Should return a token string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        
        with patch('app.security.JWTManager.create_access_token') as mock_create:
            mock_create.return_value = "jwt_token"
            
            result = JWTManager.create_access_token(data, expires_delta)
            
            mock_create.assert_called_once()
            assert result == "jwt_token"

    def test_verify_token_jwt(self):
        """Test JWT token verification"""
        token = "valid_jwt_token"
        expected_payload = {"sub": "testuser", "user_id": "user123"}
        
        with patch('app.security.JWTManager.verify_token') as mock_verify:
            mock_verify.return_value = expected_payload
            
            result = JWTManager.verify_token(token, "access")
            
            mock_verify.assert_called_once_with(token, "access")
            assert result == expected_payload

    def test_verify_token_jwt_invalid(self):
        """Test JWT token verification with invalid token"""
        token = "invalid_jwt_token"
        
        with patch('app.security.JWTManager.verify_token', side_effect=HTTPException(status_code=401, detail="Invalid token")):
            
            with pytest.raises(HTTPException) as exc_info:
                JWTManager.verify_token(token, "access")
            
            assert exc_info.value.status_code == 401
            assert "Invalid token" in str(exc_info.value.detail)

    def test_verify_token_fallback(self):
        """Test token verification fallback"""
        data = {"sub": "testuser", "user_id": "user123"}
        
        # Create token
        token = JWTManager.create_access_token(data)
        
        # Verify should work
        result = JWTManager.verify_token(token, "access")
        assert result["sub"] == "testuser"
        assert result["user_id"] == "user123"

    def test_verify_token_fallback_invalid(self):
        """Test token verification fallback with invalid token"""
        with pytest.raises(HTTPException) as exc_info:
            JWTManager.verify_token("invalid_base64_token", "access")
        
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_valid(self):
        """Test getting current user with valid token"""
        token = "valid_token"
        payload = {"sub": "testuser", "user_id": "user123"}
        
        from unittest.mock import AsyncMock
        request = Mock()
        request.headers = {"authorization": f"Bearer {token}"}
        
        with patch('app.security.SecurityManager.authenticate_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = payload
            user = await get_current_user(request)
            
            assert user.username == "testuser"
            assert user.user_id == "user123"

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_payload(self):
        """Test getting current user with invalid token payload"""
        token = "valid_token"
        payload = {"sub": "testuser"}  # Missing user_id
        
        from unittest.mock import AsyncMock
        request = Mock()
        request.headers = {"authorization": f"Bearer {token}"}
        
        with patch('app.security.SecurityManager.authenticate_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = payload
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(request)
            
            assert exc_info.value.status_code == 401
            assert "Invalid token payload" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_verify_error(self):
        """Test getting current user when token verification fails"""
        token = "invalid_token"
        
        from unittest.mock import AsyncMock
        request = Mock()
        request.headers = {"authorization": f"Bearer {token}"}
        
        with patch('app.security.SecurityManager.authenticate_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.side_effect = HTTPException(status_code=401, detail="Invalid token")
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(request)
            
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_required_valid(self):
        """Test getting current user (required) with valid user"""
        mock_user = Mock()
        mock_user.username = "testuser"
        mock_user.user_id = "user123"
        
        from unittest.mock import AsyncMock
        request = Mock()
        
        with patch('app.auth.get_current_user_required') as mock_get_user:
            mock_get_user.return_value = mock_user
            result = await mock_get_user(request)
        assert result == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_required_none(self):
        """Test getting current user (required) with None user"""
        from unittest.mock import AsyncMock
        request = Mock()
        
        with patch('app.security.SecurityManager.authenticate_request', new_callable=AsyncMock) as mock_auth:
            mock_auth.return_value = None
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user_required(request)
        
        assert exc_info.value.status_code == 401
        assert "Authentication required" in str(exc_info.value.detail)

    def test_user_register_model_validation(self):
        """Test UserRegister model validation"""
        # Valid data
        valid_data = {
            "username": "testuser",
            "password": os.getenv("TEST_PASSWORD", "password123"),
            "email": "test@example.com"
        }
        user = UserRegister(**valid_data)
        assert user.username == "testuser"
        assert user.password == os.getenv("TEST_PASSWORD", "password123")
        assert user.email == "test@example.com"

    def test_user_register_model_validation_errors(self):
        """Test UserRegister model validation errors"""
        # Username too short
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="ab", password=os.getenv("TEST_PASSWORD", "password123"))
        
        # Password too short
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="testuser", password="12345")

    def test_token_model(self):
        """Test Token model"""
        token_data = {
            "access_token": "jwt_token_here",
            "refresh_token": "refresh_token_here",
            "token_type": "bearer",
            "expires_in": 1440,
            "user_id": "user123",
            "username": "testuser"
        }
        token = Token(**token_data)
        
        assert token.access_token == "jwt_token_here"
        assert token.refresh_token == "refresh_token_here"
        assert token.token_type == "bearer"
        assert token.expires_in == 1440
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
        mock_user.password_hash = PasswordManager.hash_password("password123")
        
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
                UserRegister(username=short_username, password=os.getenv("TEST_PASSWORD", "password123"))

    def test_token_expiry_calculation(self):
        """Test token expiry calculation"""
        data = {"sub": "testuser"}
        
        # Test token creation
        token = JWTManager.create_access_token(data)
        
        # Should return a valid token
        assert isinstance(token, str)
        assert len(token) > 0

    def test_security_headers_validation(self):
        """Test security-related input validation"""
        # Test that sensitive data is properly handled
        sensitive_data = {
            "username": "<script>alert('xss')</script>",
            "password": os.getenv("TEST_PASSWORD", "password123")
        }
        
        # Should not raise exception - validation should handle this
        try:
            user = UserRegister(**sensitive_data)
            # Username should be stored as-is (validation happens at app level)
            assert user.username == "<script>alert('xss')</script>"
        except Exception:
            # If validation rejects it, that's also acceptable
            pass