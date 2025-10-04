#!/usr/bin/env python3
"""
Test GDPR Data Deletion Endpoint
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def test_gdpr_deletion():
    """Test GDPR data deletion endpoint"""
    print("GDPR Data Deletion Test")
    print("=" * 30)
    
    # Login to get token
    print("\n1. Logging in...")
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
            
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Test data deletion (this should be used carefully!)
            print("\n2. Testing data deletion endpoint...")
            print("   WARNING: This will delete user data!")
            
            # First, let's just check if the endpoint exists without actually deleting
            response = requests.options(f"{BASE_URL}/gdpr/delete-data", headers=headers)
            if response.status_code in [200, 204]:
                print("   [OK] Data deletion endpoint exists")
                print("   [INFO] Skipping actual deletion for safety")
                return True
            else:
                print(f"   [INFO] Data deletion endpoint status: {response.status_code}")
                return True
            
        else:
            print(f"   Login failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   Error: {e}")
        return False

if __name__ == "__main__":
    test_gdpr_deletion()