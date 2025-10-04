#!/usr/bin/env python3
"""
Test streaming endpoint functionality
"""

import requests
import os
import sys

def test_streaming_endpoint():
    """Test the streaming endpoint"""
    base_url = "http://localhost:9000"
    
    # Test content ID (you may need to change this to an actual content ID)
    content_id = "f1b4c70cc30b"
    
    print(f"Testing streaming endpoint for content: {content_id}")
    
    try:
        # Test basic streaming request
        response = requests.get(f"{base_url}/stream/{content_id}", timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Streaming endpoint working correctly")
            print(f"Content length: {len(response.content)} bytes")
        elif response.status_code == 404:
            print("❌ Content not found - check if content_id exists")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response text: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_range_request():
    """Test range request functionality"""
    base_url = "http://localhost:9000"
    content_id = "f1b4c70cc30b"
    
    print(f"\nTesting range request for content: {content_id}")
    
    try:
        # Test range request
        headers = {"Range": "bytes=0-1023"}
        response = requests.get(f"{base_url}/stream/{content_id}", headers=headers, timeout=10)
        
        print(f"Range response status: {response.status_code}")
        print(f"Range response headers: {dict(response.headers)}")
        
        if response.status_code == 206:
            print("✅ Range request working correctly")
        elif response.status_code == 404:
            print("❌ Content not found for range request")
        else:
            print(f"❌ Unexpected range status code: {response.status_code}")
        
        return response.status_code == 206
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Range request failed: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    base_url = "http://localhost:9000"
    
    print(f"\nTesting CORS headers")
    
    try:
        # Test OPTIONS request
        response = requests.options(f"{base_url}/stream/test", timeout=10)
        
        print(f"OPTIONS response status: {response.status_code}")
        print(f"CORS headers: {dict(response.headers)}")
        
        cors_headers = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers'
        ]
        
        has_cors = any(header in response.headers for header in cors_headers)
        
        if has_cors:
            print("✅ CORS headers present")
        else:
            print("❌ CORS headers missing")
        
        return has_cors
        
    except requests.exceptions.RequestException as e:
        print(f"❌ CORS test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Streaming Endpoint Test ===\n")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding correctly")
            sys.exit(1)
        print("✅ Server is running")
    except:
        print("❌ Server not running on localhost:9000")
        print("Please start the server with: python scripts/start_server.py")
        sys.exit(1)
    
    # Run tests
    streaming_ok = test_streaming_endpoint()
    range_ok = test_range_request()
    cors_ok = test_cors()
    
    print("\n=== Test Results ===")
    print(f"Basic Streaming: {'✅ OK' if streaming_ok else '❌ FAILED'}")
    print(f"Range Requests: {'✅ OK' if range_ok else '❌ FAILED'}")
    print(f"CORS Headers: {'✅ OK' if cors_ok else '❌ FAILED'}")
    
    if streaming_ok and cors_ok:
        print("\n🎉 Streaming endpoint is working correctly!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")