#!/usr/bin/env python3
"""
Fix authentication issues by checking for conflicting dependencies
"""

import requests
import json

def test_problematic_endpoints():
    """Test endpoints that might have authentication issues"""
    base_url = "http://localhost:9000"
    
    # Get token first
    login_data = {"username": "demo", "password": "demo1234"}
    response = requests.post(f"{base_url}/users/login", data=login_data)
    
    if response.status_code != 200:
        print("Login failed!")
        return
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test POST endpoints that require authentication
    post_endpoints = [
        ("/feedback", {"content_id": "test123", "rating": 4, "comment": "test"}),
        ("/tasks/create-test", {}),
        ("/bucket/cleanup", {"admin_key": "admin_2025"}),
    ]
    
    print("Testing POST endpoints with authentication:")
    print("=" * 50)
    
    for endpoint, data in post_endpoints:
        try:
            response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
            status = "OK" if response.status_code in [200, 201, 202] else f"ERROR {response.status_code}"
            print(f"{endpoint:<30} {status}")
            
            if response.status_code == 401:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"{endpoint:<30} ERROR: {e}")
    
    # Test file upload endpoint
    print("\nTesting file upload endpoint:")
    try:
        files = {"file": ("test.txt", "This is a test file", "text/plain")}
        data = {"title": "Test Upload", "description": "Test description"}
        response = requests.post(f"{base_url}/upload", files=files, data=data, headers=headers)
        status = "OK" if response.status_code in [200, 201] else f"ERROR {response.status_code}"
        print(f"/upload                        {status}")
        
        if response.status_code == 401:
            print(f"  Error: {response.text}")
            
    except Exception as e:
        print(f"/upload                        ERROR: {e}")

if __name__ == "__main__":
    test_problematic_endpoints()