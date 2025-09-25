#!/usr/bin/env python3
"""
Test demo login credentials
"""

import requests
import json
import time

def test_demo_login():
    """Test demo login credentials"""
    base_url = "http://127.0.0.1:8000"
    
    print("Testing demo login credentials...")
    
    # Step 1: Get demo credentials
    try:
        response = requests.get(f"{base_url}/demo-login")
        if response.status_code == 200:
            demo_data = response.json()
            print(f"[OK] Demo credentials endpoint working")
            print(f"Demo credentials: {demo_data['demo_credentials']}")
            
            username = demo_data['demo_credentials']['username']
            password = demo_data['demo_credentials']['password']
        else:
            print(f"[FAIL] Demo credentials endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Failed to get demo credentials: {e}")
        return False
    
    # Step 2: Test login
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{base_url}/users/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"[OK] Login successful!")
            print(f"Access token: {token_data['access_token'][:50]}...")
            print(f"User ID: {token_data['user_id']}")
            print(f"Username: {token_data['username']}")
            
            # Step 3: Test authenticated endpoint
            headers = {
                "Authorization": f"Bearer {token_data['access_token']}"
            }
            
            profile_response = requests.get(f"{base_url}/users/profile", headers=headers)
            if profile_response.status_code == 200:
                profile_data = profile_response.json()
                print(f"[OK] Profile access successful!")
                print(f"Profile: {json.dumps(profile_data, indent=2)}")
                return True
            else:
                print(f"[FAIL] Profile access failed: {profile_response.status_code}")
                print(f"Response: {profile_response.text}")
                return False
                
        else:
            print(f"[FAIL] Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Login test failed: {e}")
        return False

def test_database_user():
    """Test if demo user exists in database"""
    print("\nTesting database user...")
    
    try:
        from core.database import DatabaseManager
        from app.security import PasswordManager
        
        db = DatabaseManager()
        user = db.get_user_by_username('demo')
        
        if user:
            print(f"[OK] Demo user found in database: {user.user_id}")
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            
            # Test password verification
            if PasswordManager.verify_password('demo1234', user.password_hash):
                print(f"[OK] Password verification successful")
                return True
            else:
                print(f"[FAIL] Password verification failed")
                return False
        else:
            print(f"[FAIL] Demo user not found in database")
            return False
            
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Demo Login Test ===")
    
    # Test database first
    db_success = test_database_user()
    
    # Test API login
    api_success = test_demo_login()
    
    print(f"\n=== Results ===")
    print(f"Database test: {'[PASS]' if db_success else '[FAIL]'}")
    print(f"API login test: {'[PASS]' if api_success else '[FAIL]'}")
    
    if db_success and api_success:
        print(f"All tests passed! Demo login is working correctly.")
    else:
        print(f"Some tests failed. Check the issues above.")