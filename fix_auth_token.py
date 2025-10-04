#!/usr/bin/env python3
"""
Quick fix for JWT token authentication issues
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def get_fresh_token():
    """Get a fresh authentication token"""
    print("Getting fresh authentication token...")
    
    # Try demo login first
    try:
        response = requests.get(f"{BASE_URL}/demo-login")
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✓ Demo token obtained")
                return data["access_token"]
    except Exception as e:
        print(f"Demo login failed: {e}")
    
    # Try regular login
    login_data = {
        "username": "demo",
        "password": "demo1234"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login-json", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print("✓ Login token obtained")
            return data["access_token"]
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Login error: {e}")
    
    return None

def test_token(token):
    """Test if token works"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/debug-auth", headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("authenticated"):
                print("✓ Token is valid and working")
                return True
            else:
                print("✗ Token authentication failed")
                return False
        else:
            print(f"✗ Token test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Token test error: {e}")
        return False

if __name__ == "__main__":
    print("JWT Token Authentication Fix")
    print("=" * 40)
    
    # Get fresh token
    token = get_fresh_token()
    
    if token:
        print(f"\nFresh Token: {token[:50]}...")
        
        # Test the token
        if test_token(token):
            print("\n🎉 SUCCESS! Use this token in Swagger UI:")
            print(f"Bearer {token}")
            print("\nSteps to use in Swagger UI:")
            print("1. Go to http://localhost:9000/docs")
            print("2. Click the green 'Authorize' button")
            print("3. Enter the token (without 'Bearer ' prefix)")
            print("4. Click 'Authorize'")
        else:
            print("\n❌ Token is not working properly")
    else:
        print("\n❌ Could not obtain a valid token")
        print("Make sure the server is running on port 9000")