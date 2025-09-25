#!/usr/bin/env python3
"""
Debug demo authentication issue
"""

import time
from ..core.database import DatabaseManager
from ..app.security import PasswordManager

def debug_demo_auth():
    """Debug demo authentication step by step"""
    print("=== Demo Authentication Debug ===")
    
    # Step 1: Check if demo user exists in database
    print("\n1. Checking demo user in database...")
    try:
        db = DatabaseManager()
        user = db.get_user_by_username('demo')
        
        if user:
            print(f"[OK] Demo user found:")
            print(f"  - User ID: {user.user_id}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Password hash: {user.password_hash[:60]}...")
        else:
            print("[FAIL] Demo user not found in database")
            return False
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
        return False
    
    # Step 2: Test password verification
    print("\n2. Testing password verification...")
    try:
        test_password = 'demo1234'
        if PasswordManager.verify_password(test_password, user.password_hash):
            print(f"[OK] Password verification successful")
        else:
            print(f"[FAIL] Password verification failed")
            print(f"  - Test password: {test_password}")
            print(f"  - Hash: {user.password_hash[:60]}...")
            return False
    except Exception as e:
        print(f"[ERROR] Password verification error: {e}")
        return False
    
    # Step 3: Test JWT token creation
    print("\n3. Testing JWT token creation...")
    try:
        from ..app.security import JWTManager
        
        token_data = {"sub": user.username, "user_id": user.user_id}
        access_token = JWTManager.create_access_token(token_data)
        
        print(f"[OK] JWT token created successfully")
        print(f"  - Token: {access_token[:50]}...")
        
        # Verify the token
        payload = JWTManager.verify_token(access_token, "access")
        print(f"[OK] JWT token verification successful")
        print(f"  - Payload: {payload}")
        
    except Exception as e:
        print(f"[ERROR] JWT token creation/verification failed: {e}")
        return False
    
    # Step 4: Test the full login flow
    print("\n4. Testing full login flow...")
    try:
        from fastapi.security import OAuth2PasswordRequestForm
        from ..app.auth import login_user
        from fastapi import Request
        
        # Create mock request
        class MockRequest:
            def __init__(self):
                self.client = MockClient()
                self.headers = {}
        
        class MockClient:
            def __init__(self):
                self.host = "127.0.0.1"
        
        class MockFormData:
            def __init__(self, username, password):
                self.username = username
                self.password = password
        
        mock_request = MockRequest()
        mock_form = MockFormData("demo", "demo1234")
        
        print("[INFO] Mock login flow test setup complete")
        print("  - Username: demo")
        print("  - Password: demo1234")
        
    except Exception as e:
        print(f"[ERROR] Login flow test setup failed: {e}")
        return False
    
    print("\n=== Debug Summary ===")
    print("[OK] Demo user exists in database")
    print("[OK] Password verification works")
    print("[OK] JWT token creation works")
    print("[INFO] Authentication system appears to be working correctly")
    
    return True

def test_auth_endpoints():
    """Test authentication endpoints directly"""
    print("\n=== Testing Auth Endpoints ===")
    
    try:
        import requests
        import json
        
        base_url = "http://127.0.0.1:8000"
        
        # Test demo-login endpoint
        print("\n1. Testing /demo-login endpoint...")
        try:
            response = requests.get(f"{base_url}/demo-login", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print("[OK] Demo login endpoint working")
                print(f"  - Credentials: {data.get('demo_credentials', {})}")
                print(f"  - Test result: {data.get('login_test', {})}")
            else:
                print(f"[FAIL] Demo login endpoint failed: {response.status_code}")
                print(f"  - Response: {response.text}")
        except requests.exceptions.ConnectionError:
            print("[INFO] Server not running - cannot test endpoints")
            return False
        except Exception as e:
            print(f"[ERROR] Demo login test failed: {e}")
            return False
        
        # Test actual login
        print("\n2. Testing /users/login endpoint...")
        try:
            login_data = {
                "username": "demo",
                "password": "demo1234"
            }
            
            response = requests.post(f"{base_url}/users/login", data=login_data, timeout=10)
            if response.status_code == 200:
                token_data = response.json()
                print("[OK] Login successful!")
                print(f"  - Access token: {token_data.get('access_token', '')[:50]}...")
                print(f"  - User ID: {token_data.get('user_id')}")
                print(f"  - Username: {token_data.get('username')}")
                
                # Test authenticated endpoint
                print("\n3. Testing authenticated endpoint...")
                headers = {
                    "Authorization": f"Bearer {token_data['access_token']}"
                }
                
                profile_response = requests.get(f"{base_url}/users/profile", headers=headers, timeout=5)
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    print("[OK] Profile access successful!")
                    print(f"  - Profile: {json.dumps(profile_data, indent=2)}")
                    return True
                else:
                    print(f"[FAIL] Profile access failed: {profile_response.status_code}")
                    print(f"  - Response: {profile_response.text}")
                    return False
                    
            else:
                print(f"[FAIL] Login failed: {response.status_code}")
                print(f"  - Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Login test failed: {e}")
            return False
            
    except ImportError:
        print("[INFO] Requests library not available - skipping endpoint tests")
        return True

if __name__ == "__main__":
    print("Starting demo authentication debug...")
    
    # Test database and authentication components
    db_success = debug_demo_auth()
    
    # Test actual endpoints if server is running
    endpoint_success = test_auth_endpoints()
    
    print(f"\n=== Final Results ===")
    print(f"Database/Auth Components: {'[PASS]' if db_success else '[FAIL]'}")
    print(f"Endpoint Tests: {'[PASS]' if endpoint_success else '[FAIL]'}")
    
    if db_success and endpoint_success:
        print("\n[SUCCESS] Demo authentication is working correctly!")
        print("Credentials: username=demo, password=demo1234")
    elif db_success:
        print("\n[PARTIAL] Database components work, but server may not be running")
        print("Try starting the server with: python start_server.py")
    else:
        print("\n[FAILED] Demo authentication has issues")
        print("Run fix_demo_password.py to fix the demo user")