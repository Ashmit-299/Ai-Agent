#!/usr/bin/env python3
"""Debug JWT token issues"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./debug.db")
os.environ.setdefault("JWT_SECRET_KEY", "debug-secret-key")

def test_jwt_flow():
    """Test JWT creation and verification"""
    
    print("=== JWT Debug Test ===")
    
    try:
        from app.security import JWTManager
        
        # Test token creation
        print("1. Testing token creation...")
        token_data = {"sub": "testuser", "user_id": "user_123"}
        access_token = JWTManager.create_access_token(token_data)
        print(f"Token created: {access_token[:50]}...")
        
        # Test token verification
        print("\n2. Testing token verification...")
        payload = JWTManager.verify_token(access_token, "access")
        print(f"Token verified: {payload}")
        
        # Test with Bearer prefix
        print("\n3. Testing with Bearer prefix...")
        bearer_token = f"Bearer {access_token}"
        print(f"Bearer token: {bearer_token[:50]}...")
        
        # Extract token from Bearer
        if bearer_token.startswith("Bearer "):
            token_only = bearer_token[7:]  # Remove "Bearer " prefix
            payload2 = JWTManager.verify_token(token_only, "access")
            print(f"Bearer token verified: {payload2}")
        
        print("\n[SUCCESS] JWT flow working correctly!")
        return access_token
        
    except Exception as e:
        print(f"[ERROR] JWT test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    token = test_jwt_flow()
    if token:
        print(f"\nUse this token for testing: {token}")
        print(f"In Swagger, enter: {token}")
        print("(Don't include 'Bearer' prefix in Swagger)")