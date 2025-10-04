#!/usr/bin/env python3
"""Test complete authentication flow"""

import requests
import json
import time

BASE_URL = "http://localhost:9000"

def test_auth_flow():
    """Test registration -> login -> profile access"""
    
    # Step 1: Register user
    print("=== Step 1: Registration ===")
    register_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "TestPassword123!",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/users/register", json=register_data)
    print(f"Registration Status: {response.status_code}")
    
    if response.status_code == 201:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"Access Token: {access_token[:50]}...")
        
        # Step 2: Test profile access with token
        print("\n=== Step 2: Profile Access ===")
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        profile_response = requests.get(f"{BASE_URL}/users/profile", headers=headers)
        print(f"Profile Status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            print(f"Profile Data: {json.dumps(profile_data, indent=2)}")
            print("[SUCCESS] Authentication flow working!")
        else:
            print(f"Profile Error: {profile_response.text}")
            
        # Step 3: Test other endpoints
        print("\n=== Step 3: Test Other Endpoints ===")
        
        # Test health endpoint (no auth required)
        health_response = requests.get(f"{BASE_URL}/health")
        print(f"Health Status: {health_response.status_code}")
        
        # Test metrics endpoint (may require auth)
        metrics_response = requests.get(f"{BASE_URL}/metrics", headers=headers)
        print(f"Metrics Status: {metrics_response.status_code}")
        
    else:
        print(f"Registration failed: {response.text}")

if __name__ == "__main__":
    test_auth_flow()