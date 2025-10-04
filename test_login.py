#!/usr/bin/env python3
"""
Test login functionality with existing user credentials
"""

import requests
import json

def test_login():
    """Test login with existing user credentials"""
    base_url = "http://localhost:9000"
    
    # Test credentials
    credentials = {
        "username": "ashmit",
        "password": "Ashmit@123"
    }
    
    print("Testing login endpoints...")
    
    # Test JSON login endpoint
    try:
        response = requests.post(
            f"{base_url}/users/login",
            json=credentials,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"JSON Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Login successful!")
            print(f"  - User ID: {data.get('user_id')}")
            print(f"  - Username: {data.get('username')}")
            print(f"  - Token Type: {data.get('token_type')}")
            print(f"  - Access Token: {data.get('access_token')[:20]}...")
            return data.get('access_token')
        else:
            print(f"✗ Login failed: {response.text}")
            
    except Exception as e:
        print(f"✗ JSON Login error: {e}")
    
    # Test form login endpoint
    try:
        response = requests.post(
            f"{base_url}/users/login-form",
            data=credentials,  # Form data
            timeout=10
        )
        
        print(f"Form Login Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Form login successful!")
            return data.get('access_token')
        else:
            print(f"✗ Form login failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Form Login error: {e}")
    
    return None

def test_authenticated_endpoint(token):
    """Test an authenticated endpoint with the token"""
    if not token:
        print("No token available for testing")
        return
    
    base_url = "http://localhost:9000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{base_url}/users/profile",
            headers=headers,
            timeout=10
        )
        
        print(f"Profile Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Profile access successful!")
            print(f"  - Profile: {json.dumps(data, indent=2)}")
        else:
            print(f"✗ Profile access failed: {response.text}")
            
    except Exception as e:
        print(f"✗ Profile access error: {e}")

if __name__ == "__main__":
    print("=== Login Test ===")
    token = test_login()
    
    print("\n=== Authenticated Endpoint Test ===")
    test_authenticated_endpoint(token)