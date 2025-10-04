#!/usr/bin/env python3
"""
Test Individual Endpoints
"""
import requests
import json

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        print(f"{description}: {response.status_code}")
        
        if response.status_code == 200:
            try:
                # Try to parse as JSON
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)[:200]}...")
            except:
                # If not JSON, show text
                text = response.text[:200]
                print(f"  Response: {text}...")
        else:
            print(f"  Error: {response.text[:100]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"{description}: ERROR - {e}")
        return False

def test_all_endpoints():
    """Test key endpoints"""
    
    base_url = "http://127.0.0.1:9000"
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/test", "Test endpoint"),
        ("/docs", "API documentation"),
        ("/openapi.json", "OpenAPI spec"),
        ("/demo-login", "Demo login"),
    ]
    
    print("TESTING ENDPOINTS")
    print("=" * 40)
    
    results = []
    for path, desc in endpoints:
        url = f"{base_url}{path}"
        result = test_endpoint(url, desc)
        results.append((path, result))
        print("-" * 30)
    
    print("\nSUMMARY:")
    print("=" * 40)
    for path, result in results:
        status = "WORKING" if result else "FAILED"
        print(f"{path}: {status}")
    
    # Check if root is working
    root_working = results[0][1] if results else False
    if not root_working:
        print("\nROOT ENDPOINT ISSUE DETECTED!")
        print("This explains the white screen.")

if __name__ == "__main__":
    test_all_endpoints()