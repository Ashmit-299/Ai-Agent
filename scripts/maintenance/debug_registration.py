#!/usr/bin/env python3
"""Debug registration endpoint"""

import os
import sys
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./debug.db")
os.environ.setdefault("JWT_SECRET_KEY", "debug-secret-key")

def test_registration_components():
    """Test each component of registration"""
    
    print("=== Testing Registration Components ===")
    
    try:
        print("1. Testing imports...")
        from ..app.models import UserRegister
        from ..app.security import PasswordManager, JWTManager, InputSanitizer
        from ..core.database import DatabaseManager
        print("[OK] Imports successful")
        
        print("\n2. Testing user data validation...")
        user_data = UserRegister(
            username="testuser123",
            password="TestPassword123!",
            email="test@example.com"
        )
        print(f"[OK] User data: {user_data.username}")
        
        print("\n3. Testing input sanitization...")
        username = InputSanitizer.sanitize_string(user_data.username, 50)
        print(f"[OK] Sanitized username: {username}")
        
        print("\n4. Testing password validation...")
        validation = PasswordManager.validate_password_strength(user_data.password)
        print(f"[OK] Password valid: {validation['valid']}")
        if not validation['valid']:
            print(f"Issues: {validation['issues']}")
            
        print("\n5. Testing password hashing...")
        password_hash = PasswordManager.hash_password(user_data.password)
        print(f"[OK] Password hashed: {password_hash[:20]}...")
        
        print("\n6. Testing database manager...")
        db = DatabaseManager()
        print("[OK] Database manager created")
        
        print("\n7. Testing user creation...")
        import uuid
        import time
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        user_dict = {
            "user_id": user_id,
            "username": username,
            "password_hash": password_hash,
            "email": user_data.email,
            "email_verified": False,
            "created_at": time.time()
        }
        
        new_user = db.create_user(user_dict)
        print(f"[OK] User created: {new_user.username}")
        
        print("\n8. Testing JWT token creation...")
        token_data = {"sub": username, "user_id": user_id}
        access_token = JWTManager.create_access_token(token_data)
        refresh_token = JWTManager.create_refresh_token(user_id)
        print(f"[OK] Tokens created: {len(access_token)} chars")
        
        print("\n[SUCCESS] All components working!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Error in component test: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

def test_full_registration():
    """Test the full registration endpoint"""
    
    print("\n=== Testing Full Registration Endpoint ===")
    
    try:
        from fastapi import Request
        from ..app.auth import register_user
        from ..app.models import UserRegister
        
        # Create mock request
        class MockRequest:
            def __init__(self):
                self.client = type('obj', (object,), {'host': '127.0.0.1'})()
                self.headers = {}
        
        request = MockRequest()
        
        # Create user data
        user_data = UserRegister(
            username=f"testuser_{int(time.time())}",
            password="TestPassword123!",
            email="test@example.com"
        )
        
        print(f"Testing registration for: {user_data.username}")
        
        # Call registration function
        import asyncio
        result = asyncio.run(register_user(user_data, request))
        
        print(f"[SUCCESS] Registration successful!")
        print(f"User ID: {result.user_id}")
        print(f"Username: {result.username}")
        print(f"Token type: {result.token_type}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Full registration test failed: {e}")
        print(f"Traceback:\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    import time
    
    # Test components first
    components_ok = test_registration_components()
    
    if components_ok:
        # Test full registration
        test_full_registration()
    else:
        print("[ERROR] Component tests failed, skipping full test")