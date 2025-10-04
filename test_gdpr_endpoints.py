#!/usr/bin/env python3
"""
Test script to verify GDPR endpoints work with authentication
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:9000"

def test_gdpr_endpoints():
    """Test GDPR endpoints with authentication"""
    print("🔒 Testing GDPR Endpoints with Authentication")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("1. Registering test user...")
    register_data = {
        "username": f"gdpr_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "email": f"gdpr_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            print("✅ User registered successfully")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Step 2: Login to get JWT token
    print("2. Logging in to get JWT token...")
    login_data = {
        "username": register_data["username"],
        "password": register_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ Login successful, token obtained")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Headers with authentication
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 3: Test GDPR Privacy Policy (public endpoint)
    print("3. Testing GDPR Privacy Policy...")
    try:
        response = requests.get(f"{BASE_URL}/gdpr/privacy-policy")
        if response.status_code == 200:
            print("✅ Privacy policy accessible")
        else:
            print(f"❌ Privacy policy failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Privacy policy error: {e}")
    
    # Step 4: Test Data Summary (authenticated)
    print("4. Testing Data Summary...")
    try:
        response = requests.get(f"{BASE_URL}/gdpr/data-summary", headers=headers)
        if response.status_code == 200:
            data_summary = response.json()
            print("✅ Data summary retrieved successfully")
            print(f"   User ID: {data_summary.get('user_id')}")
            print(f"   Data types: {len(data_summary.get('data_types', []))}")
        else:
            print(f"❌ Data summary failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Data summary error: {e}")
    
    # Step 5: Test Data Export (authenticated)
    print("5. Testing Data Export...")
    try:
        response = requests.get(f"{BASE_URL}/gdpr/export-data", headers=headers)
        if response.status_code == 200:
            export_data = response.json()
            print("✅ Data export successful")
            print(f"   Export contains: {list(export_data.keys())}")
        else:
            print(f"❌ Data export failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Data export error: {e}")
    
    # Step 6: Test without authentication (should fail)
    print("6. Testing endpoints without authentication...")
    try:
        response = requests.get(f"{BASE_URL}/gdpr/data-summary")
        if response.status_code == 401:
            print("✅ Correctly rejected unauthenticated request")
        else:
            print(f"❌ Should have rejected unauthenticated request: {response.status_code}")
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
    
    # Step 7: Test Data Deletion (authenticated) - WARNING: This will delete the user
    print("7. Testing Data Deletion (WARNING: This deletes the test user)...")
    try:
        response = requests.delete(f"{BASE_URL}/gdpr/delete-data", headers=headers)
        if response.status_code == 200:
            delete_result = response.json()
            print("✅ Data deletion successful")
            print(f"   Deleted items: {delete_result.get('deleted_items', 0)}")
        else:
            print(f"❌ Data deletion failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Data deletion error: {e}")
    
    print("\n🎯 GDPR Endpoint Testing Complete!")
    return True

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 GDPR Endpoints Test Script")
    print("=" * 50)
    
    # Check if server is running
    if not check_server_status():
        print("❌ Server is not running on port 9000")
        print("Please start the server first:")
        print("python scripts/start_server.py")
        sys.exit(1)
    
    print("✅ Server is running")
    
    # Run GDPR tests
    success = test_gdpr_endpoints()
    
    if success:
        print("\n🎉 All GDPR endpoint tests completed!")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)