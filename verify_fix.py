#!/usr/bin/env python3
"""
Verify that the authentication fix is working
"""

import requests

def verify_fix():
    """Verify all endpoints are working with authentication"""
    base_url = "http://localhost:9000"
    
    print("=== AUTHENTICATION FIX VERIFICATION ===")
    
    # Get token
    login_data = {"username": "demo", "password": "demo1234"}
    response = requests.post(f"{base_url}/users/login", data=login_data)
    
    if response.status_code != 200:
        print("FAILED: Could not login")
        return False
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print(f"SUCCESS: Got authentication token")
    
    # Test the specific endpoints mentioned by user
    endpoints_to_test = [
        ("GET", "/contents"),
        ("POST", "/upload", {"files": {"file": ("test.txt", "test content", "text/plain")}, "data": {"title": "Test", "description": "Test"}}),
        ("POST", "/feedback", {"json": {"content_id": "test", "rating": 4, "comment": "test"}}),
        ("POST", "/generate-video", {"files": {"file": ("script.txt", "Test script content", "text/plain")}, "data": {"title": "Test Video"}}),
        ("GET", "/metrics"),
    ]
    
    all_working = True
    
    for method, endpoint, *kwargs in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == "POST":
                extra_args = kwargs[0] if kwargs else {}
                if "files" in extra_args:
                    response = requests.post(f"{base_url}{endpoint}", 
                                           files=extra_args["files"], 
                                           data=extra_args["data"], 
                                           headers=headers)
                elif "json" in extra_args:
                    response = requests.post(f"{base_url}{endpoint}", 
                                           json=extra_args["json"], 
                                           headers=headers)
                else:
                    response = requests.post(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code in [200, 201, 202]:
                print(f"SUCCESS: {method} {endpoint} - Status {response.status_code}")
            elif response.status_code == 401:
                print(f"FAILED: {method} {endpoint} - Still getting 401 Unauthorized")
                print(f"        Response: {response.text}")
                all_working = False
            else:
                print(f"WARNING: {method} {endpoint} - Status {response.status_code} (not 401)")
                
        except Exception as e:
            print(f"ERROR: {method} {endpoint} - Exception: {e}")
            all_working = False
    
    print("\n" + "=" * 50)
    if all_working:
        print("SUCCESS: All endpoints are working with authentication!")
        print("The 401 'Authentication required' errors have been fixed.")
        print("\nNext steps:")
        print("1. Make sure you're authorized in Swagger UI")
        print("2. Use the token from /users/login in the Authorization header")
        print("3. All protected endpoints should now work correctly")
    else:
        print("FAILED: Some endpoints are still showing authentication errors")
    
    return all_working

if __name__ == "__main__":
    verify_fix()