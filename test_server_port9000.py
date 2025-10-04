#!/usr/bin/env python3
"""
Test server connectivity on port 9000 and verify monitoring integration
"""

import requests
import json

def test_port_9000():
    """Test all endpoints on port 9000"""
    
    base_url = "http://localhost:9000"
    
    print("Testing AI-Agent Server on Port 9000")
    print("=" * 50)
    
    endpoints = [
        "/health",
        "/test", 
        "/docs",
        "/monitoring-status",
        "/test-monitoring"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "OK" if response.status_code == 200 else f"HTTP {response.status_code}"
            print(f"{status:<10} {endpoint}")
            
            if endpoint == "/test" and response.status_code == 200:
                data = response.json()
                print(f"           Server: {data.get('message', 'Unknown')}")
                
        except requests.exceptions.ConnectionError:
            print(f"OFFLINE    {endpoint} - Server not running")
        except Exception as e:
            print(f"ERROR      {endpoint} - {str(e)}")
    
    print("=" * 50)
    print(f"Main Server URL: {base_url}")
    print(f"API Documentation: {base_url}/docs")
    print(f"Dashboard: {base_url}/dashboard")

if __name__ == "__main__":
    test_port_9000()