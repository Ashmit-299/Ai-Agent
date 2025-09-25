#!/usr/bin/env python3
"""
Test script for registration endpoint
"""

import requests
import json
import time

def test_registration():
    """Test the registration endpoint"""
    
    # Test data
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "password": "TestPassword123!",
        "email": "test@example.com"
    }
    
    # API endpoint
    url = "http://localhost:9000/users/register"
    
    try:
        print("Testing registration endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_user, indent=2)}")
        
        # Make request
        response = requests.post(url, json=test_user, timeout=10)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Response Body (raw): {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            return True
        else:
            print("❌ Registration failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - is the server running on port 9000?")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_registration()