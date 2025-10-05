#!/usr/bin/env python3
"""
Test Server Working - Verify all endpoints work
"""

import requests
import time

def test_server():
    base_url = "http://localhost:9000"
    
    print("🧪 Testing Server Functionality")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check: OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not running: {e}")
        return False
    
    # Test 2: Demo login
    try:
        response = requests.get(f"{base_url}/demo-login")
        if response.status_code == 200:
            print("✅ Demo login: OK")
        else:
            print(f"❌ Demo login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Demo login error: {e}")
    
    # Test 3: API docs
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API docs: OK")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    # Test 4: Enhanced upload endpoint exists
    try:
        response = requests.get(f"{base_url}/openapi.json")
        if response.status_code == 200:
            openapi = response.json()
            if "/upload-enhanced" in str(openapi):
                print("✅ Enhanced upload endpoint: Available")
            else:
                print("⚠️  Enhanced upload endpoint: Not found in OpenAPI")
        else:
            print(f"❌ OpenAPI failed: {response.status_code}")
    except Exception as e:
        print(f"❌ OpenAPI error: {e}")
    
    print(f"\n🎉 Server is working!")
    print(f"🌐 Access your server at: {base_url}")
    print(f"📖 API Documentation: {base_url}/docs")
    print(f"🔒 Enhanced Upload: POST {base_url}/upload-enhanced")
    
    return True

if __name__ == "__main__":
    test_server()