#!/usr/bin/env python3
"""
Test all the endpoints mentioned by the user
"""

import requests
import json

def test_all_endpoints():
    """Test all endpoints that were showing 401 errors"""
    base_url = "http://localhost:9000"
    
    # Get fresh token
    login_data = {"username": "demo", "password": "demo1234"}
    response = requests.post(f"{base_url}/users/login", data=login_data)
    
    if response.status_code != 200:
        print("Login failed!")
        return False
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("Testing all endpoints mentioned by user:")
    print("=" * 60)
    
    # Test GET endpoints
    get_endpoints = [
        "/contents",
        "/metrics", 
    ]
    
    for endpoint in get_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            status = "OK" if response.status_code == 200 else f"ERROR {response.status_code}"
            print(f"GET  {endpoint:<30} {status}")
            
            if response.status_code == 401:
                print(f"     401 Error: {response.text}")
                
        except Exception as e:
            print(f"GET  {endpoint:<30} ERROR: {e}")
    
    # Test POST endpoints
    print("\nTesting POST endpoints:")
    
    # Test feedback
    try:
        feedback_data = {"content_id": "test123", "rating": 4, "comment": "test feedback"}
        response = requests.post(f"{base_url}/feedback", json=feedback_data, headers=headers)
        status = "OK" if response.status_code in [200, 201] else f"ERROR {response.status_code}"
        print(f"POST /feedback                 {status}")
        
        if response.status_code == 401:
            print(f"     401 Error: {response.text}")
            
    except Exception as e:
        print(f"POST /feedback                 ERROR: {e}")
    
    # Test file upload
    try:
        files = {"file": ("test.txt", "This is a test script for video generation", "text/plain")}
        data = {"title": "Test Upload", "description": "Test description"}
        response = requests.post(f"{base_url}/upload", files=files, data=data, headers=headers)
        status = "OK" if response.status_code in [200, 201] else f"ERROR {response.status_code}"
        print(f"POST /upload                   {status}")
        
        if response.status_code == 401:
            print(f"     401 Error: {response.text}")
            
    except Exception as e:
        print(f"POST /upload                   ERROR: {e}")
    
    # Test video generation
    try:
        files = {"file": ("script.txt", "Hello world. This is a test script. Generate video from this.", "text/plain")}
        data = {"title": "Test Video"}
        response = requests.post(f"{base_url}/generate-video", files=files, data=data, headers=headers)
        status = "OK" if response.status_code in [200, 201, 202] else f"ERROR {response.status_code}"
        print(f"POST /generate-video           {status}")
        
        if response.status_code == 401:
            print(f"     401 Error: {response.text}")
            
    except Exception as e:
        print(f"POST /generate-video           ERROR: {e}")
    
    # Test content access endpoints (need content_id)
    print("\nTesting content access endpoints:")
    
    # First get a content ID
    try:
        contents_response = requests.get(f"{base_url}/contents", headers=headers)
        if contents_response.status_code == 200:
            contents_data = contents_response.json()
            items = contents_data.get("items", [])
            
            if items:
                content_id = items[0]["content_id"]
                
                # Test content endpoints
                content_endpoints = [
                    f"/content/{content_id}",
                    f"/download/{content_id}",
                    f"/stream/{content_id}"
                ]
                
                for endpoint in content_endpoints:
                    try:
                        response = requests.get(f"{base_url}{endpoint}", headers=headers)
                        status = "OK" if response.status_code in [200, 206] else f"ERROR {response.status_code}"
                        print(f"GET  {endpoint:<30} {status}")
                        
                        if response.status_code == 401:
                            print(f"     401 Error: {response.text}")
                            
                    except Exception as e:
                        print(f"GET  {endpoint:<30} ERROR: {e}")
            else:
                print("No content available to test content access endpoints")
        else:
            print("Could not get contents list")
            
    except Exception as e:
        print(f"Content access test failed: {e}")
    
    print("\n" + "=" * 60)
    print("All endpoint tests completed!")
    return True

if __name__ == "__main__":
    test_all_endpoints()