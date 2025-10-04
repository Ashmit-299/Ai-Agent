#!/usr/bin/env python3
"""
Test script to verify Swagger UI is working properly
"""

import requests
import json
import time

def test_docs_endpoints():
    """Test all documentation endpoints"""
    base_url = "http://localhost:9000"
    
    endpoints = {
        "OpenAPI JSON": "/openapi.json",
        "Swagger UI": "/docs", 
        "ReDoc": "/redoc",
        "Root": "/",
        "Health": "/health"
    }
    
    print("Testing documentation endpoints...")
    
    for name, endpoint in endpoints.items():
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {name} ({endpoint}): {response.status_code}")
            
            if endpoint == "/openapi.json" and response.status_code == 200:
                try:
                    data = response.json()
                    paths_count = len(data.get("paths", {}))
                    print(f"  - Found {paths_count} API endpoints")
                    
                    # Check for security schemes
                    security_schemes = data.get("components", {}).get("securitySchemes", {})
                    if security_schemes:
                        print(f"  - Security schemes: {list(security_schemes.keys())}")
                    
                except Exception as e:
                    print(f"  - JSON parsing error: {e}")
                    
        except requests.exceptions.RequestException as e:
            print(f"✗ {name} ({endpoint}): Connection failed - {e}")
    
    print(f"\nTest completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_docs_endpoints()