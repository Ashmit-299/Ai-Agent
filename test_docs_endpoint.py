#!/usr/bin/env python3
"""
Test Docs Endpoint Specifically
"""
import requests

def test_docs_endpoints():
    """Test docs-related endpoints"""
    
    base_url = "http://127.0.0.1:9000"
    
    endpoints = [
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
        ("/openapi.json", "OpenAPI JSON")
    ]
    
    print("DOCS ENDPOINT TEST")
    print("=" * 30)
    
    for path, name in endpoints:
        try:
            response = requests.get(f"{base_url}{path}", timeout=10)
            print(f"{name}: Status {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', 'unknown')
                print(f"  Content-Type: {content_type}")
                print(f"  Content Length: {len(response.text)} chars")
                
                if path == "/openapi.json":
                    # Check if valid JSON
                    try:
                        import json
                        data = response.json()
                        print(f"  OpenAPI Version: {data.get('openapi', 'unknown')}")
                        print(f"  Title: {data.get('info', {}).get('title', 'unknown')}")
                        paths_count = len(data.get('paths', {}))
                        print(f"  API Paths: {paths_count}")
                    except:
                        print("  ERROR: Invalid JSON")
                
                elif path == "/docs":
                    # Check Swagger UI content
                    if "swagger-ui" in response.text.lower():
                        print("  Contains Swagger UI references")
                    if "openapi.json" in response.text:
                        print("  References OpenAPI spec")
                    if len(response.text) < 1000:
                        print("  WARNING: Content seems too short")
                        print(f"  First 200 chars: {response.text[:200]}")
            else:
                print(f"  ERROR: {response.text[:100]}")
                
        except Exception as e:
            print(f"{name}: ERROR - {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_docs_endpoints()