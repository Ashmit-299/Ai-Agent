#!/usr/bin/env python3
"""
Test script to verify streaming endpoint fixes
"""

import requests
import json

def test_streaming_endpoint():
    """Test the streaming endpoint with proper content types"""
    
    base_url = "http://localhost:9000"
    
    # Test content ID from your example
    content_id = "f1b4c70cc30b"
    
    print("Testing streaming endpoint fixes...")
    print(f"Content ID: {content_id}")
    
    # Test streaming endpoint
    stream_url = f"{base_url}/stream/{content_id}"
    
    try:
        # Make request without range header first
        print(f"\n1. Testing full file streaming: {stream_url}")
        response = requests.get(stream_url, stream=True)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"Content-Length: {response.headers.get('Content-Length', 'Not set')}")
        print(f"Accept-Ranges: {response.headers.get('Accept-Ranges', 'Not set')}")
        
        # Check if it's a video MIME type
        content_type = response.headers.get('Content-Type', '')
        if content_type.startswith('video/'):
            print("✅ SUCCESS: Content-Type is video/* - should show preview in browser")
        elif content_type == 'application/octet-stream':
            print("❌ ISSUE: Content-Type is application/octet-stream - will force download")
        else:
            print(f"ℹ️  INFO: Content-Type is {content_type}")
        
        # Test with range header
        print(f"\n2. Testing range request streaming:")
        headers = {'Range': 'bytes=0-1023'}
        range_response = requests.get(stream_url, headers=headers, stream=True)
        
        print(f"Range Status Code: {range_response.status_code}")
        print(f"Range Content-Type: {range_response.headers.get('Content-Type', 'Not set')}")
        print(f"Content-Range: {range_response.headers.get('Content-Range', 'Not set')}")
        
        if range_response.status_code == 206:
            print("✅ SUCCESS: Range requests working (206 Partial Content)")
        else:
            print(f"❌ ISSUE: Range request failed with status {range_response.status_code}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure it's running on port 9000")
        print("Run: python scripts/start_server.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_content_endpoint():
    """Test the content metadata endpoint"""
    
    base_url = "http://localhost:9000"
    content_id = "f1b4c70cc30b"
    
    print(f"\n3. Testing content metadata endpoint:")
    content_url = f"{base_url}/content/{content_id}"
    
    try:
        response = requests.get(content_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Content Type: {data.get('content_type', 'Not set')}")
            print(f"Stream URL: {data.get('stream_url', 'Not set')}")
            print(f"Download URL: {data.get('download_url', 'Not set')}")
            print("✅ SUCCESS: Content metadata retrieved")
        else:
            print(f"❌ ISSUE: Content not found or error occurred")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🔧 Streaming Endpoint Fix Test")
    print("=" * 50)
    
    success = test_streaming_endpoint()
    if success:
        test_content_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nExpected behavior:")
    print("- Video files (.mp4) should have Content-Type: video/mp4")
    print("- Browser should show video preview instead of download")
    print("- Range requests should return 206 status code")
    print("- Accept-Ranges: bytes header should be present")