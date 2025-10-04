#!/usr/bin/env python3
"""
Test if server needs restart for Prometheus integration
"""

import requests
import time

def test_server_status():
    """Test current server status"""
    base_url = "http://localhost:9000"
    
    print("Testing Server Status...")
    print("=" * 30)
    
    try:
        # Test basic health
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health endpoint: {response.status_code}")
        
        # Test debug routes to see current routes
        response = requests.get(f"{base_url}/debug-routes", timeout=5)
        if response.status_code == 200:
            data = response.json()
            routes = [r['path'] for r in data.get('all_routes', [])]
            
            metrics_routes = [r for r in routes if 'metrics' in r]
            print(f"Metrics routes found: {metrics_routes}")
            
            if '/metrics' in routes:
                print("✓ /metrics route exists")
            else:
                print("✗ /metrics route missing")
                
            if '/metrics/prometheus' in routes:
                print("✓ /metrics/prometheus route exists")
            else:
                print("✗ /metrics/prometheus route missing")
        
        # Test metrics endpoints directly
        endpoints_to_test = ['/metrics', '/metrics/prometheus', '/metrics/performance']
        
        for endpoint in endpoints_to_test:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                print(f"{endpoint}: {response.status_code}")
            except Exception as e:
                print(f"{endpoint}: ERROR - {e}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Test server status"""
    print("Server Status Check for Prometheus Integration")
    print("=" * 50)
    
    server_ok = test_server_status()
    
    if server_ok:
        print("\nServer is running. If metrics endpoints are missing,")
        print("restart the server to pick up Prometheus integration:")
        print("1. Stop current server (Ctrl+C)")
        print("2. Run: python scripts/start_server.py")
    else:
        print("\nServer not running. Start with:")
        print("python scripts/start_server.py")

if __name__ == "__main__":
    main()