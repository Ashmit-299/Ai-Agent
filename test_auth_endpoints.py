#!/usr/bin/env python3
"""
Test authentication endpoints with JWKS integration
"""

import requests
import json
import time

def test_auth_endpoints():
    """Test authentication endpoints"""
    base_url = "http://localhost:9000"
    
    print("Testing Authentication Endpoints...")
    print("=" * 50)
    
    # Test 1: Supabase auth health
    try:
        response = requests.get(f"{base_url}/users/supabase-auth-health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK: Supabase auth health endpoint")
            print(f"Status: {data.get('status')}")
            print(f"JWKS URL configured: {data.get('supabase_integration', {}).get('jwks_url')}")
        else:
            print(f"ERROR: Supabase auth health - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Supabase auth health test failed: {e}")
    
    # Test 2: Enhanced debug auth
    try:
        response = requests.get(f"{base_url}/debug-auth", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK: Enhanced debug auth endpoint")
            print(f"Supported auth types: {data.get('supported_auth_types', [])}")
        else:
            print(f"ERROR: Debug auth - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Debug auth test failed: {e}")
    
    # Test 3: Login and test token
    try:
        login_data = {"username": "demo", "password": "demo1234"}
        response = requests.post(f"{base_url}/users/login", data=login_data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            print("OK: Login successful")
            
            # Test token with debug auth
            headers = {"Authorization": f"Bearer {token_data['access_token']}"}
            auth_response = requests.get(f"{base_url}/debug-auth", headers=headers, timeout=10)
            
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                print(f"OK: Token authentication - Type: {auth_data.get('auth_type')}")
                print(f"User: {auth_data.get('username')} (ID: {auth_data.get('user_id')})")
            else:
                print(f"ERROR: Token auth test - {auth_response.status_code}")
        else:
            print(f"ERROR: Login failed - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Login test failed: {e}")
    
    # Test 4: Health check with auth status
    try:
        response = requests.get(f"{base_url}/health/detailed", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("OK: Detailed health check")
            if "supabase_auth" in data:
                supabase_auth = data["supabase_auth"]
                print(f"Supabase auth available: {supabase_auth.get('supabase_url_configured', False)}")
        else:
            print(f"ERROR: Health check - {response.status_code}")
    except Exception as e:
        print(f"ERROR: Health check test failed: {e}")

def main():
    """Run authentication endpoint tests"""
    print("Authentication Endpoints Test")
    print("=" * 50)
    print("Make sure the server is running on port 9000")
    print("Start with: python scripts/start_server.py")
    print()
    
    try:
        # Check if server is running
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("Server is running, proceeding with tests...")
            test_auth_endpoints()
        else:
            print("Server responded but not healthy")
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running on port 9000")
        print("Start the server with: python scripts/start_server.py")
    except Exception as e:
        print(f"ERROR: Server check failed: {e}")

if __name__ == "__main__":
    main()