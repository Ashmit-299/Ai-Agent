#!/usr/bin/env python3
"""
Final Endpoint Test - Simple Version
"""
import requests

def test_endpoints():
    """Test key endpoints"""
    
    base_url = "http://127.0.0.1:9000"
    
    endpoints = [
        ("/", "Root Page"),
        ("/health", "Health Check"),
        ("/docs", "API Docs"),
        ("/test", "Test Endpoint"),
        ("/demo-login", "Demo Login")
    ]
    
    print("ENDPOINT TEST RESULTS")
    print("=" * 40)
    
    all_working = True
    
    for path, name in endpoints:
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            if response.status_code == 200:
                print(f"{name}: WORKING (200)")
            else:
                print(f"{name}: ERROR ({response.status_code})")
                all_working = False
        except Exception as e:
            print(f"{name}: FAILED - {str(e)[:50]}")
            all_working = False
    
    print("=" * 40)
    
    if all_working:
        print("SUCCESS: All endpoints working!")
        print("\nYour AI Agent is ready:")
        print(f"- Main Page: {base_url}")
        print(f"- API Docs: {base_url}/docs")
        print(f"- Health: {base_url}/health")
        print("\nIf you still see white screen:")
        print("1. Hard refresh browser (Ctrl+F5)")
        print("2. Clear browser cache")
        print("3. Try incognito/private mode")
        print("4. Check browser console for errors")
    else:
        print("ERROR: Some endpoints not working")
    
    return all_working

if __name__ == "__main__":
    test_endpoints()