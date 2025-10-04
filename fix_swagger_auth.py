#!/usr/bin/env python3
"""
Fix Swagger UI authorization issues
"""

import requests
import json
import time

def get_fresh_token():
    """Get a fresh authentication token"""
    base_url = "http://localhost:9000"
    
    print("Getting fresh authentication token...")
    login_data = {"username": "demo", "password": "demo1234"}
    
    try:
        response = requests.post(f"{base_url}/users/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            print(f"✓ Fresh token obtained")
            print(f"Token: {access_token}")
            print(f"Expires in: {token_data.get('expires_in', 1440)} minutes")
            
            # Test the token immediately
            headers = {"Authorization": f"Bearer {access_token}"}
            test_response = requests.get(f"{base_url}/debug-auth", headers=headers)
            
            if test_response.status_code == 200:
                debug_data = test_response.json()
                if debug_data.get("authenticated"):
                    print("✓ Token validation successful")
                    print("\nSwagger UI Authorization Steps:")
                    print("1. Go to http://localhost:9000/docs")
                    print("2. Click the green 'Authorize' button at the top")
                    print("3. In the 'Value' field, enter ONLY the token (no 'Bearer ' prefix):")
                    print(f"   {access_token}")
                    print("4. Click 'Authorize' button")
                    print("5. Click 'Close' button")
                    print("6. Now all protected endpoints should work")
                    
                    return access_token
                else:
                    print("✗ Token validation failed")
                    print(f"Debug response: {debug_data}")
            else:
                print(f"✗ Token test failed: {test_response.status_code}")
                print(f"Response: {test_response.text}")
        else:
            print(f"✗ Login failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
    
    return None

def test_all_protected_endpoints(token):
    """Test all protected endpoints with the token"""
    base_url = "http://localhost:9000"
    headers = {"Authorization": f"Bearer {token}"}
    
    protected_endpoints = [
        ("GET", "/contents"),
        ("GET", "/metrics"),
        ("GET", "/observability/performance"),
        ("GET", "/users/profile"),
        ("POST", "/feedback", {"content_id": "test", "rating": 4}),
        ("GET", "/rl/agent-stats"),
        ("GET", "/bhiv/analytics"),
        ("GET", "/bucket/stats"),
    ]
    
    print("\nTesting all protected endpoints:")
    print("=" * 60)
    
    all_working = True
    
    for method, endpoint, *data in protected_endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == "POST":
                payload = data[0] if data else {}
                response = requests.post(f"{base_url}{endpoint}", json=payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                status = "✓ OK"
            elif response.status_code == 401:
                status = "✗ 401 UNAUTHORIZED"
                all_working = False
            else:
                status = f"? {response.status_code}"
            
            print(f"{method:<4} {endpoint:<30} {status}")
            
            if response.status_code == 401:
                print(f"     Error: {response.text}")
                
        except Exception as e:
            print(f"{method:<4} {endpoint:<30} ✗ ERROR: {e}")
            all_working = False
    
    if all_working:
        print("\n✓ All endpoints working correctly!")
        print("If you're still seeing 401 errors in Swagger UI:")
        print("1. Clear browser cache and cookies")
        print("2. Refresh the /docs page")
        print("3. Re-authorize with the fresh token")
    else:
        print("\n✗ Some endpoints still have authentication issues")
        print("This indicates a server-side authentication problem")

if __name__ == "__main__":
    print("=== Authentication Troubleshooting Tool ===")
    token = get_fresh_token()
    
    if token:
        test_all_protected_endpoints(token)
    else:
        print("\nFailed to get authentication token")
        print("Check if the server is running and demo user exists")