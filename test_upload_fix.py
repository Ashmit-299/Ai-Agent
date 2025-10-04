#!/usr/bin/env python3
"""
Test Upload Fix - Verify Supabase Content Saving
"""

import os
import sys
import time
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def test_upload_endpoint():
    """Test the upload endpoint with a real file"""
    print("[INFO] Testing upload endpoint...")
    
    # Create a test file
    test_content = "This is a test script for upload verification.\nTesting Supabase database saving functionality."
    test_filename = "test_upload.txt"
    
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    try:
        # First get demo credentials
        demo_response = requests.get("http://localhost:8000/demo-login")
        if demo_response.status_code != 200:
            print("[ERROR] Could not get demo credentials")
            return False
        
        demo_data = demo_response.json()
        username = demo_data["demo_credentials"]["username"]
        password = demo_data["demo_credentials"]["password"]
        
        # Login to get token
        login_data = {"username": username, "password": password}
        login_response = requests.post("http://localhost:8000/users/login", data=login_data)
        
        if login_response.status_code != 200:
            print(f"[ERROR] Login failed: {login_response.status_code}")
            return False
        
        token_data = login_response.json()
        access_token = token_data["access_token"]
        
        # Upload file
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": open(test_filename, "rb")}
        data = {"title": "Test Upload Fix", "description": "Testing Supabase upload"}
        
        upload_response = requests.post(
            "http://localhost:8000/upload",
            headers=headers,
            files=files,
            data=data
        )
        
        files["file"].close()
        
        if upload_response.status_code == 201:
            result = upload_response.json()
            content_id = result["content_id"]
            print(f"[SUCCESS] Upload successful! Content ID: {content_id}")
            
            # Verify in database
            return verify_in_database(content_id)
        else:
            print(f"[ERROR] Upload failed: {upload_response.status_code}")
            print(f"Response: {upload_response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Upload test failed: {e}")
        return False
    finally:
        # Clean up test file
        try:
            os.remove(test_filename)
        except:
            pass

def verify_in_database(content_id):
    """Verify content was saved to Supabase"""
    print(f"[INFO] Verifying content {content_id} in database...")
    
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("SELECT title, uploader_id FROM content WHERE content_id = %s", (content_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            print(f"[SUCCESS] Content found in Supabase: {result[0]} by {result[1]}")
            return True
        else:
            print("[ERROR] Content not found in Supabase database")
            return False
            
    except Exception as e:
        print(f"[ERROR] Database verification failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Upload Fix")
    print("=" * 30)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("[ERROR] Server not responding properly")
            return False
    except:
        print("[ERROR] Server not running on localhost:8000")
        print("Please start the server first: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return False
    
    # Test upload
    success = test_upload_endpoint()
    
    if success:
        print("\n[SUCCESS] Upload fix working correctly!")
        print("Content is being saved to Supabase database.")
    else:
        print("\n[ERROR] Upload fix needs more work.")
        print("Check server logs for detailed error messages.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)