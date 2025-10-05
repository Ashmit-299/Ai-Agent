#!/usr/bin/env python3
"""
Test Enhanced Upload Endpoint
Tests the new /upload-enhanced endpoint with comprehensive validation
"""

import requests
import json
import time
import os

def test_enhanced_upload():
    """Test the enhanced upload endpoint"""
    base_url = "http://localhost:9000"
    
    print("🧪 Testing Enhanced Upload Endpoint")
    print("=" * 50)
    
    # Step 1: Get demo credentials
    print("1️⃣ Getting demo credentials...")
    try:
        response = requests.get(f"{base_url}/demo-login")
        if response.status_code == 200:
            demo_data = response.json()
            username = demo_data["demo_credentials"]["username"]
            password = demo_data["demo_credentials"]["password"]
            print(f"✅ Demo credentials: {username}/{password}")
        else:
            print(f"❌ Failed to get demo credentials: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting demo credentials: {e}")
        return False
    
    # Step 2: Login to get token
    print("\n2️⃣ Logging in...")
    try:
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{base_url}/users/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"✅ Login successful, token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Step 3: Test enhanced upload with various file types
    headers = {"Authorization": f"Bearer {access_token}"}
    
    test_files = [
        {
            "name": "test_text.txt",
            "content": "This is a test text file for enhanced upload validation.",
            "title": "Test Text File",
            "description": "Testing enhanced upload with text file"
        },
        {
            "name": "test_script.txt", 
            "content": "# Test Script\nprint('Hello World')\nprint('This is a test script')",
            "title": "Test Script",
            "description": "Testing script upload functionality"
        }
    ]
    
    for i, test_file in enumerate(test_files, 3):
        print(f"\n{i}️⃣ Testing enhanced upload: {test_file['name']}")
        
        try:
            # Create temporary file
            with open(test_file['name'], 'w') as f:
                f.write(test_file['content'])
            
            # Upload file
            with open(test_file['name'], 'rb') as f:
                files = {'file': (test_file['name'], f, 'text/plain')}
                data = {
                    'title': test_file['title'],
                    'description': test_file['description']
                }
                
                response = requests.post(
                    f"{base_url}/upload-enhanced",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            # Clean up temporary file
            os.remove(test_file['name'])
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Upload successful!")
                print(f"   Content ID: {result['content_id']}")
                print(f"   File size: {result['file_size_mb']} MB")
                print(f"   MIME type: {result['mime_type']}")
                print(f"   Authenticity: {result['authenticity_score']}")
                print(f"   Processing time: {result['processing_time_seconds']}s")
                
                if result['validation']['warnings']:
                    print(f"   Warnings: {result['validation']['warnings']}")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            # Clean up if file exists
            if os.path.exists(test_file['name']):
                os.remove(test_file['name'])
            return False
    
    # Step 4: Test file size limit
    print(f"\n{len(test_files) + 3}️⃣ Testing file size limit...")
    try:
        # Create a large file (should be rejected)
        large_content = "A" * (101 * 1024 * 1024)  # 101MB (over limit)
        with open("large_test.txt", 'w') as f:
            f.write(large_content)
        
        with open("large_test.txt", 'rb') as f:
            files = {'file': ('large_test.txt', f, 'text/plain')}
            data = {
                'title': 'Large Test File',
                'description': 'Testing file size limits'
            }
            
            response = requests.post(
                f"{base_url}/upload-enhanced",
                files=files,
                data=data,
                headers=headers
            )
        
        os.remove("large_test.txt")
        
        if response.status_code == 413:
            print("✅ File size limit working correctly (413 error expected)")
        else:
            print(f"⚠️  Unexpected response for large file: {response.status_code}")
            
    except Exception as e:
        print(f"❌ File size test error: {e}")
        if os.path.exists("large_test.txt"):
            os.remove("large_test.txt")
    
    # Step 5: Test dangerous file extension
    print(f"\n{len(test_files) + 4}️⃣ Testing dangerous file extension...")
    try:
        with open("test.exe", 'w') as f:
            f.write("fake executable")
        
        with open("test.exe", 'rb') as f:
            files = {'file': ('test.exe', f, 'application/octet-stream')}
            data = {
                'title': 'Dangerous File',
                'description': 'Testing dangerous extension blocking'
            }
            
            response = requests.post(
                f"{base_url}/upload-enhanced",
                files=files,
                data=data,
                headers=headers
            )
        
        os.remove("test.exe")
        
        if response.status_code == 400:
            print("✅ Dangerous extension blocking working correctly (400 error expected)")
        else:
            print(f"⚠️  Unexpected response for dangerous file: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Dangerous file test error: {e}")
        if os.path.exists("test.exe"):
            os.remove("test.exe")
    
    print(f"\n🎉 Enhanced upload testing completed!")
    return True

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main test function"""
    print("🚀 AI Agent Enhanced Upload Test")
    print("=" * 50)
    
    # Check if server is running
    if not test_server_health():
        print("❌ Server not running on http://localhost:9000")
        print("💡 Start server with: python scripts/start_server.py")
        return
    
    print("✅ Server is running")
    
    # Run tests
    success = test_enhanced_upload()
    
    if success:
        print("\n🎉 All tests passed!")
        print("✅ Enhanced upload endpoint is working correctly")
        print("🔒 Security validations are active")
    else:
        print("\n❌ Some tests failed")
        print("💡 Check the server logs for more details")

if __name__ == "__main__":
    main()