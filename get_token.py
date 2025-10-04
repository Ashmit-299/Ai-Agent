#!/usr/bin/env python3
"""
Get fresh JWT token for authentication
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def get_token():
    """Get authentication token"""
    print("Getting authentication token...")
    
    # Try demo login
    try:
        response = requests.get(f"{BASE_URL}/demo-login")
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                token = data["access_token"]
                print("SUCCESS: Demo token obtained")
                print(f"Token: {token}")
                print("\nTo use in Swagger UI:")
                print("1. Go to http://localhost:9000/docs")
                print("2. Click 'Authorize' button")
                print(f"3. Enter: {token}")
                print("4. Click 'Authorize'")
                return token
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
            token = data["access_token"]
            print("SUCCESS: Login token obtained")
            print(f"Token: {token}")
            print("\nTo use in Swagger UI:")
            print("1. Go to http://localhost:9000/docs")
            print("2. Click 'Authorize' button")
            print(f"3. Enter: {token}")
            print("4. Click 'Authorize'")
            return token
        else:
            print(f"Login failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Login error: {e}")
    
    print("FAILED: Could not get token")
    return None

if __name__ == "__main__":
    get_token()