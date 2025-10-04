#!/usr/bin/env python3
"""
Test all GDPR endpoints with fresh token
"""

import requests
import json

BASE_URL = "http://localhost:9000"

def test_all_gdpr_endpoints():
    """Test all GDPR endpoints"""
    print("Testing All GDPR Endpoints")
    print("=" * 40)
    
    # Get fresh token
    print("\n1. Getting fresh token...")
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
    
    # Test all endpoints
    endpoints = [
        ("GET", "/gdpr/privacy-policy", None, "Privacy Policy"),
        ("GET", "/gdpr/data-summary", headers, "Data Summary"),
        ("GET", "/gdpr/export-data", headers, "Data Export"),
        ("DELETE", "/gdpr/delete-data", headers, "Data Deletion")
    ]
    
    print("\n2. Testing endpoints...")
    results = {}
    
    for method, endpoint, auth_headers, name in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", headers=auth_headers)
            elif method == "DELETE":
                # For delete, we need to send confirmation data
                data = {"confirm_deletion": False, "reason": "test"}
                response = requests.delete(f"{BASE_URL}{endpoint}", json=data, headers=auth_headers)
            
            if response.status_code in [200, 400]:  # 400 is expected for delete without confirmation
                print(f"   [OK] {name}: {response.status_code}")
                results[name] = "OK"
            else:
                print(f"   [FAIL] {name}: {response.status_code} - {response.text[:100]}")
                results[name] = f"FAIL ({response.status_code})"
                
        except Exception as e:
            print(f"   [ERROR] {name}: {e}")
            results[name] = f"ERROR ({e})"
    
    print(f"\n3. Results Summary:")
    for name, result in results.items():
        print(f"   {name}: {result}")
    
    return all("OK" in result for result in results.values())

if __name__ == "__main__":
    success = test_all_gdpr_endpoints()
    if success:
        print("\n[SUCCESS] All GDPR endpoints working!")
    else:
        print("\n[PARTIAL] Some endpoints may have issues")