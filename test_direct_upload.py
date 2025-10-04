#!/usr/bin/env python3
"""
Test Direct Upload Functionality
"""
import requests
import json
import os
import tempfile

# Configuration
BASE_URL = "http://localhost:9000"
USERNAME = "demo"
PASSWORD = "demo1234"

def test_direct_upload():
    """Test the new direct upload functionality"""
    
    print("Testing Direct Upload Functionality")
    print("=" * 50)
    
    # Step 1: Login to get JWT token
    print("1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code != 200:
        print(f"[ERROR] Login failed: {login_response.status_code}")
        print(login_response.text)
        return False
    
    token_data = login_response.json()
    jwt_token = token_data["access_token"]
    print(f"[SUCCESS] Login successful, token: {jwt_token[:20]}...")
    
    # Step 2: Get upload URL
    print("\n2. Getting upload URL...")
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    upload_url_response = requests.get(
        f"{BASE_URL}/cdn/upload-url",
        params={
            "filename": "test_file.txt",
            "content_type": "text/plain"
        },
        headers=headers
    )
    
    if upload_url_response.status_code != 200:
        print(f"[ERROR] Upload URL generation failed: {upload_url_response.status_code}")
        print(upload_url_response.text)
        return False
    
    upload_data = upload_url_response.json()
    print(f"[SUCCESS] Upload URL generated:")
    print(f"   Method: {upload_data['method']}")
    print(f"   Upload URL: {upload_data['upload_url']}")
    print(f"   Expires in: {upload_data['expires_in']} seconds")
    
    # Step 3: Create test file
    print("\n3. Creating test file...")
    test_content = "Hello, this is a test file for direct upload functionality!"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        test_file_path = f.name
    
    print(f"[SUCCESS] Test file created: {test_file_path}")
    
    # Step 4: Upload file using the provided URL
    print("\n4. Uploading file...")
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('test_file.txt', f, 'text/plain')}
            
            upload_response = requests.post(
                upload_data['upload_url'],
                files=files,
                headers=headers
            )
        
        if upload_response.status_code not in [200, 201]:
            print(f"[ERROR] File upload failed: {upload_response.status_code}")
            print(upload_response.text)
            return False
        
        upload_result = upload_response.json()
        print(f"[SUCCESS] File uploaded successfully:")
        print(f"   Content ID: {upload_result.get('content_id')}")
        print(f"   Filename: {upload_result.get('filename')}")
        print(f"   File size: {upload_result.get('file_size')} bytes")
        print(f"   Download URL: {upload_result.get('download_url')}")
        
        # Step 5: Test download
        print("\n5. Testing download...")
        if upload_result.get('download_url'):
            download_response = requests.get(
                f"{BASE_URL}{upload_result['download_url']}",
                headers=headers
            )
            
            if download_response.status_code == 200:
                downloaded_content = download_response.text
                if downloaded_content == test_content:
                    print("[SUCCESS] Download successful and content matches!")
                else:
                    print("[WARNING] Download successful but content doesn't match")
                    print(f"Expected: {test_content}")
                    print(f"Got: {downloaded_content}")
            else:
                print(f"[ERROR] Download failed: {download_response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Upload error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.unlink(test_file_path)

def test_upload_with_curl():
    """Generate curl command for testing"""
    
    print("\n" + "=" * 50)
    print("CURL Command Example")
    print("=" * 50)
    
    # Get token first
    login_response = requests.post(
        f"{BASE_URL}/login",
        data={"username": USERNAME, "password": PASSWORD},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        jwt_token = token_data["access_token"]
        
        # Get upload URL
        headers = {"Authorization": f"Bearer {jwt_token}"}
        upload_url_response = requests.get(
            f"{BASE_URL}/cdn/upload-url",
            params={
                "filename": "my_file.txt",
                "content_type": "text/plain"
            },
            headers=headers
        )
        
        if upload_url_response.status_code == 200:
            upload_data = upload_url_response.json()
            
            print("1. Get upload URL:")
            print(f"""curl -X GET '{BASE_URL}/cdn/upload-url?filename=my_file.txt&content_type=text%2Fplain' \\
  -H 'Authorization: Bearer {jwt_token}'""")
            
            print("\n2. Upload file:")
            print(f"""curl -X POST '{upload_data["upload_url"]}' \\
  -H 'Authorization: Bearer {jwt_token}' \\
  -F 'file=@my_file.txt'""")
            
            print(f"\n3. Example response from upload URL:")
            print(json.dumps(upload_data, indent=2))

if __name__ == "__main__":
    success = test_direct_upload()
    test_upload_with_curl()
    
    print("\n" + "=" * 50)
    if success:
        print("[SUCCESS] All tests passed! Direct upload is working correctly.")
    else:
        print("[ERROR] Some tests failed. Check the output above.")
    print("=" * 50)