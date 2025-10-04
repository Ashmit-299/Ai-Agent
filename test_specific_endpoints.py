#!/usr/bin/env python3
"""
Test specific endpoints that might be showing 401 errors
"""

import requests
import json

def test_endpoints():
    """Test specific endpoints with authentication"""
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
    
    # Test endpoints that might be problematic
    endpoints_to_test = [
        "/contents",
        "/metrics", 
        "/observability/performance",
        "/rl/agent-stats",
        "/streaming-performance",
        "/bucket/stats",
        "/bhiv/analytics"
    ]
    
    print("Testing endpoints with authentication:")
    print("=" * 50)
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
            print(f"{endpoint:<30} {status}")
            
            if response.status_code == 401:
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"{endpoint:<30} ERROR: {e}")

if __name__ == "__main__":
    test_endpoints()