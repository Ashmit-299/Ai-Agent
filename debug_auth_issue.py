#!/usr/bin/env python3
"""
Debug authentication issue - test JWT token verification
"""

import os
import sys
import time
import requests
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_auth_flow():
    """Test the complete authentication flow"""
    base_url = "http://localhost:9000"
    
    print("=== Testing Authentication Flow ===")
    
    # Step 1: Login to get token
    print("\n1. Testing login...")
    login_data = {
        "username": "demo",
        "password": "demo1234"
    }
    
    try:
        response = requests.post(f"{base_url}/users/login", data=login_data)
        print(f"Login status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"Access token received: {access_token[:50]}...")
            
            # Step 2: Test protected endpoint
            print("\n2. Testing protected endpoint...")
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test /upload endpoint
            test_response = requests.get(f"{base_url}/contents", headers=headers)
            print(f"Protected endpoint status: {test_response.status_code}")
            
            if test_response.status_code != 200:
                print(f"Error response: {test_response.text}")
                
                # Step 3: Debug token verification
                print("\n3. Debugging token verification...")
                try:
                    from app.security import JWTManager
                    payload = JWTManager.verify_token(access_token, "access")
                    print(f"Token payload: {payload}")
                except Exception as e:
                    print(f"Token verification error: {e}")
                    
                # Step 4: Test auth debug endpoint
                print("\n4. Testing auth debug endpoint...")
                debug_response = requests.get(f"{base_url}/debug-auth", headers=headers)
                print(f"Debug auth status: {debug_response.status_code}")
                if debug_response.status_code == 200:
                    print(f"Debug auth response: {debug_response.json()}")
            else:
                print("✅ Authentication working correctly!")
                
        else:
            print(f"Login failed: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_auth_flow()