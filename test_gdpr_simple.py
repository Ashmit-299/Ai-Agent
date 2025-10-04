#!/usr/bin/env python3
"""
Simple GDPR Endpoints Test Script
Tests authentication and GDPR endpoint functionality
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:9000"

def test_gdpr_endpoints():
    """Test GDPR endpoints with authentication"""
    print("GDPR Endpoints Test Script")
    print("=" * 50)
    
    # Step 1: Register a test user
    print("\n1. Registering test user...")
    register_data = {
        "username": "gdpr_test_user",
        "email": "gdpr@test.com",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/register", json=register_data)
        if response.status_code == 200:
            print("   User registered successfully")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   User already exists, continuing...")
        else:
            print(f"   Registration failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   Registration error: {e}")
    
    # Step 2: Login to get token
    print("\n2. Logging in...")
    login_data = {
        "username": "gdpr_test_user",
        "password": "TestPassword123!"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/users/login-json", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("   Login successful")
            
            # Headers for authenticated requests
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Step 3: Test GDPR endpoints
            print("\n3. Testing GDPR endpoints...")
            
            # Test privacy policy (public)
            print("   Testing privacy policy...")
            response = requests.get(f"{BASE_URL}/gdpr/privacy-policy")
            if response.status_code == 200:
                print("   [OK] Privacy policy accessible")
            else:
                print(f"   [FAIL] Privacy policy failed: {response.status_code}")
            
            # Test data summary (authenticated)
            print("   Testing data summary...")
            response = requests.get(f"{BASE_URL}/gdpr/data-summary", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"   [OK] Data summary retrieved: {len(data)} items")
            else:
                print(f"   [FAIL] Data summary failed: {response.status_code}")
            
            # Test data export (authenticated)
            print("   Testing data export...")
            response = requests.get(f"{BASE_URL}/gdpr/export-data", headers=headers)
            if response.status_code == 200:
                print("   [OK] Data export successful")
            else:
                print(f"   [FAIL] Data export failed: {response.status_code}")
            
            print("\n4. GDPR endpoints test completed!")
            return True
            
        else:
            print(f"   Login failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"   Login error: {e}")
        return False

def check_server_status():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    if not check_server_status():
        print("Server is not running on port 9000!")
        print("Please start the server first: python scripts/start_server.py")
        sys.exit(1)
    
    success = test_gdpr_endpoints()
    sys.exit(0 if success else 1)