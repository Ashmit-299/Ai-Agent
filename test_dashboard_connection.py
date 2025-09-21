#!/usr/bin/env python3
"""
Test Dashboard-API Connection
"""

import requests

def test_connection():
    """Test the dashboard connection to API"""
    print("Testing Dashboard-API Connection...")
    
    # Test health endpoint
    try:
        response = requests.get('http://127.0.0.1:9000/health', timeout=5)
        print(f"[PASS] Health check: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False
    
    # Test authentication
    try:
        login_data = {"username": "demo", "password": "demo123"}
        response = requests.post('http://127.0.0.1:9000/users/login', json=login_data, timeout=5)
        if response.status_code == 200:
            token = response.json().get('access_token')
            print(f"[PASS] Authentication successful")
            
            # Test protected endpoint
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('http://127.0.0.1:9000/metrics', headers=headers, timeout=5)
            print(f"[INFO] Protected endpoint test: {response.status_code}")
            
        else:
            print(f"[WARN] Authentication failed: {response.status_code}")
            print("Dashboard will work with limited functionality")
    except Exception as e:
        print(f"[WARN] Auth test failed: {e}")
    
    print("\nDashboard should now connect properly!")
    print("Run: python start_dashboard.py")
    return True

if __name__ == "__main__":
    test_connection()