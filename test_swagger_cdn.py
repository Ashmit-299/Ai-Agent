#!/usr/bin/env python3
"""
Test Swagger UI CDN endpoints
"""
import requests

BASE_URL = "http://localhost:9000"

def test_swagger_endpoints():
    """Check what CDN endpoints are available in Swagger"""
    print("Checking Swagger UI CDN Endpoints")
    print("=" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            
            # Find CDN endpoints
            cdn_endpoints = []
            for path, methods in openapi_data.get("paths", {}).items():
                if path.startswith("/cdn/"):
                    for method in methods.keys():
                        cdn_endpoints.append(f"{method.upper()} {path}")
            
            print(f"\nFound {len(cdn_endpoints)} CDN endpoints:")
            for endpoint in sorted(cdn_endpoints):
                print(f"  {endpoint}")
            
            # Check for problematic endpoint
            problematic = "/cdn/direct-upload/{upload_token}"
            if any(problematic in endpoint for endpoint in cdn_endpoints):
                print(f"\n❌ PROBLEM: Found old endpoint: {problematic}")
                print("   This causes URL encoding issues in Swagger UI")
            else:
                print(f"\n✅ GOOD: No problematic endpoints found")
                print("   All CDN endpoints should work correctly")
            
            return True
        else:
            print(f"Failed to get OpenAPI spec: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_swagger_endpoints()