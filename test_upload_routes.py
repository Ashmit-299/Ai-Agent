#!/usr/bin/env python3
"""
Test script to verify upload routes and debug routing conflicts
"""
import requests
import json
import time

BASE_URL = "http://localhost:9000"

def test_route_enumeration():
    """Test the debug routes endpoint"""
    print("=== Testing Route Enumeration ===")
    try:
        response = requests.get(f"{BASE_URL}/debug-routes")
        if response.status_code == 200:
            data = response.json()
            print(f"Total routes: {data['total_routes']}")
            print(f"Upload routes found: {len(data['upload_routes'])}")
            for route in data['upload_routes']:
                print(f"  - {route['methods']} {route['path']}")
        else:
            print(f"Failed to get routes: {response.status_code}")
    except Exception as e:
        print(f"Error testing routes: {e}")

def test_demo_login():
    """Get demo credentials and login"""
    print("\n=== Testing Demo Login ===")
    try:
        # Get demo credentials
        response = requests.get(f"{BASE_URL}/demo-login")
        if response.status_code == 200:
            data = response.json()
            username = data['demo_credentials']['username']
            password = data['demo_credentials']['password']
            print(f"Demo credentials: {username}/{password}")
            
            # Login
            login_response = requests.post(f"{BASE_URL}/users/login", json={
                "username": username,
                "password": password
            })
            
            if login_response.status_code == 200:
                token = login_response.json()['access_token']
                print(f"Login successful, token: {token[:20]}...")
                return token
            else:
                print(f"Login failed: {login_response.status_code} - {login_response.text}")
                return None
        else:
            print(f"Failed to get demo credentials: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error in demo login: {e}")
        return None

def test_cdn_upload_url(token):
    """Test CDN upload URL generation"""
    print("\n=== Testing CDN Upload URL Generation ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/cdn/upload-url", 
                              params={"filename": "test.txt", "content_type": "text/plain"},
                              headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Upload URL generated: {data['upload_url']}")
            print(f"Upload token: {data['upload_token']}")
            return data['upload_token']
        else:
            print(f"Failed to get upload URL: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error getting upload URL: {e}")
        return None

def test_cdn_upload(token, upload_token):
    """Test CDN file upload"""
    print("\n=== Testing CDN File Upload ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test file content
        test_content = "This is a test file for upload debugging"
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = requests.post(f"{BASE_URL}/cdn/upload/{upload_token}",
                               files=files,
                               headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Upload successful: {data['content_id']}")
            print(f"File path: {data['file_path']}")
            return data['content_id']
        else:
            print(f"Upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error in upload: {e}")
        return None

def test_main_upload(token):
    """Test main upload endpoint"""
    print("\n=== Testing Main Upload Endpoint ===")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Create test file content
        test_content = "This is a test file for main upload endpoint"
        files = {"file": ("test_main.txt", test_content, "text/plain")}
        data = {"title": "Test Main Upload", "description": "Testing main upload route"}
        
        response = requests.post(f"{BASE_URL}/upload",
                               files=files,
                               data=data,
                               headers=headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"Main upload successful: {result['content_id']}")
            print(f"File path: {result['file_path']}")
            return result['content_id']
        else:
            print(f"Main upload failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error in main upload: {e}")
        return None

def test_health_check():
    """Test basic health check"""
    print("\n=== Testing Health Check ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"Health check passed: {data['status']}")
            return True
        else:
            print(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error in health check: {e}")
        return False

def main():
    """Run all tests"""
    print("Starting upload route debugging tests...")
    print(f"Testing against: {BASE_URL}")
    
    # Test basic connectivity
    if not test_health_check():
        print("Server not responding, exiting...")
        return
    
    # Test route enumeration
    test_route_enumeration()
    
    # Get authentication token
    token = test_demo_login()
    if not token:
        print("Could not get authentication token, skipping upload tests...")
        return
    
    # Test CDN upload flow
    upload_token = test_cdn_upload_url(token)
    if upload_token:
        test_cdn_upload(token, upload_token)
    
    # Test main upload endpoint
    test_main_upload(token)
    
    print("\n=== Test Summary ===")
    print("All tests completed. Check output above for any failures.")

if __name__ == "__main__":
    main()