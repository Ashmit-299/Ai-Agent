#!/usr/bin/env python3
"""
Test simplified CDN endpoints
"""
import requests
import io

BASE_URL = "http://localhost:9000"

def test_cdn_workflow():
    """Test complete CDN workflow"""
    print("Testing Simplified CDN Endpoints")
    print("=" * 40)
    
    # 1. Get authentication token
    print("\n1. Getting authentication token...")
    try:
        response = requests.post(f"{BASE_URL}/users/login-json", json={
            "username": "demo",
            "password": "demo1234"
        })
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("   [OK] Token obtained")
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print(f"   [FAIL] Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # 2. Get upload URL
    print("\n2. Getting upload URL...")
    try:
        response = requests.get(
            f"{BASE_URL}/cdn/upload-url",
            params={"filename": "test.txt", "content_type": "text/plain"},
            headers=headers
        )
        if response.status_code == 200:
            upload_data = response.json()
            upload_url = upload_data["upload_url"]
            print(f"   [OK] Upload URL: {upload_url}")
        else:
            print(f"   [FAIL] Upload URL failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # 3. Upload file
    print("\n3. Uploading test file...")
    try:
        test_content = "Hello, this is a test file for CDN upload!"
        files = {"file": ("test.txt", io.BytesIO(test_content.encode()), "text/plain")}
        
        response = requests.post(
            f"{BASE_URL}{upload_url}",
            files=files,
            headers=headers
        )
        if response.status_code == 200:
            upload_result = response.json()
            content_id = upload_result["content_id"]
            print(f"   [OK] File uploaded: {content_id}")
        else:
            print(f"   [FAIL] Upload failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # 4. Test file info
    print("\n4. Getting file info...")
    try:
        response = requests.get(f"{BASE_URL}/cdn/info/{content_id}", headers=headers)
        if response.status_code == 200:
            file_info = response.json()
            print(f"   [OK] File info: {file_info['filename']}")
        else:
            print(f"   [FAIL] File info failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # 5. Test download
    print("\n5. Testing download...")
    try:
        response = requests.get(f"{BASE_URL}/cdn/download/{content_id}", headers=headers)
        if response.status_code == 200:
            downloaded_content = response.text
            if test_content in downloaded_content:
                print("   [OK] Download successful and content matches")
            else:
                print("   [WARN] Download successful but content differs")
        else:
            print(f"   [FAIL] Download failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # 6. Test list files
    print("\n6. Testing file list...")
    try:
        response = requests.get(f"{BASE_URL}/cdn/list", headers=headers)
        if response.status_code == 200:
            file_list = response.json()
            print(f"   [OK] Found {len(file_list['files'])} files")
        else:
            print(f"   [FAIL] List failed: {response.status_code}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n7. CDN workflow test completed!")
    return True

if __name__ == "__main__":
    # Check server
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Server not responding properly!")
            exit(1)
    except:
        print("Server is not running on port 9000!")
        print("Please start: python scripts/start_server.py")
        exit(1)
    
    test_cdn_workflow()