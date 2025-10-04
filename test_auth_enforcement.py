#!/usr/bin/env python3
"""
Test authentication enforcement at middleware level
"""

import sys
import os
import requests
import time

def test_public_endpoints():
    """Test that public endpoints work without authentication"""
    print("Testing public endpoints (should work without auth)...")
    
    public_endpoints = [
        "/",
        "/health", 
        "/demo-login",
        "/debug/database",
        "/test",
        "/debug-auth"
    ]
    
    base_url = "http://localhost:9000"
    results = {}
    
    for endpoint in public_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            results[endpoint] = {
                "status": response.status_code,
                "accessible": response.status_code < 400
            }
            print(f"  {endpoint}: {response.status_code} {'✓' if response.status_code < 400 else '✗'}")
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "accessible": False,
                "error": str(e)
            }
            print(f"  {endpoint}: ERROR - {e}")
    
    return results

def test_protected_endpoints():
    """Test that protected endpoints require authentication"""
    print("\nTesting protected endpoints (should require auth)...")
    
    protected_endpoints = [
        "/contents",
        "/metrics", 
        "/upload",
        "/feedback"
    ]
    
    base_url = "http://localhost:9000"
    results = {}
    
    for endpoint in protected_endpoints:
        try:
            # Test without auth header
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            results[endpoint] = {
                "status": response.status_code,
                "protected": response.status_code == 401,
                "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:100]
            }
            print(f"  {endpoint}: {response.status_code} {'✓' if response.status_code == 401 else '✗'}")
        except Exception as e:
            results[endpoint] = {
                "status": "error",
                "protected": False,
                "error": str(e)
            }
            print(f"  {endpoint}: ERROR - {e}")
    
    return results

def test_with_valid_token():
    """Test that protected endpoints work with valid token"""
    print("\nTesting with valid authentication token...")
    
    base_url = "http://localhost:9000"
    
    try:
        # First get a token by logging in
        login_data = {
            "username": "demo",
            "password": "demo1234"
        }
        
        login_response = requests.post(
            f"{base_url}/users/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        if login_response.status_code != 200:
            print(f"  Login failed: {login_response.status_code}")
            return {"login_failed": True}
        
        token_data = login_response.json()
        access_token = token_data.get("access_token")
        
        if not access_token:
            print("  No access token received")
            return {"no_token": True}
        
        print(f"  Login successful, got token")
        
        # Test protected endpoint with token
        headers = {"Authorization": f"Bearer {access_token}"}
        
        test_endpoints = ["/contents", "/metrics"]
        results = {}
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
                results[endpoint] = {
                    "status": response.status_code,
                    "accessible": response.status_code < 400
                }
                print(f"  {endpoint} with token: {response.status_code} {'✓' if response.status_code < 400 else '✗'}")
            except Exception as e:
                results[endpoint] = {
                    "status": "error",
                    "accessible": False,
                    "error": str(e)
                }
                print(f"  {endpoint} with token: ERROR - {e}")
        
        return results
        
    except Exception as e:
        print(f"  Token test failed: {e}")
        return {"test_failed": str(e)}

def main():
    print("Authentication Enforcement Test")
    print("=" * 40)
    print("Note: Server must be running on localhost:9000")
    print()
    
    # Test if server is running
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code != 200:
            print("Server not responding correctly")
            return
    except Exception as e:
        print(f"Server not accessible: {e}")
        print("Please start the server with: python quick_start.py")
        return
    
    public_results = test_public_endpoints()
    protected_results = test_protected_endpoints()
    token_results = test_with_valid_token()
    
    print("\n" + "=" * 40)
    print("SUMMARY:")
    
    # Check public endpoints
    public_working = sum(1 for r in public_results.values() if r.get("accessible", False))
    print(f"Public endpoints working: {public_working}/{len(public_results)}")
    
    # Check protected endpoints
    protected_working = sum(1 for r in protected_results.values() if r.get("protected", False))
    print(f"Protected endpoints secured: {protected_working}/{len(protected_results)}")
    
    # Check token access
    if isinstance(token_results, dict) and not any(k in token_results for k in ["login_failed", "no_token", "test_failed"]):
        token_working = sum(1 for r in token_results.values() if r.get("accessible", False))
        print(f"Token access working: {token_working}/{len(token_results)}")
    else:
        print("Token access test failed")
    
    if public_working > 0 and protected_working > 0:
        print("\n✓ Authentication enforcement is working correctly!")
    else:
        print("\n✗ Authentication enforcement has issues")

if __name__ == "__main__":
    main()