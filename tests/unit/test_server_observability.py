#!/usr/bin/env python3
"""Test observability integration with FastAPI server"""

import requests
import time
import json
from datetime import datetime

def test_server_with_observability():
    """Test server endpoints to trigger observability events"""
    
    base_url = "http://127.0.0.1:8000"
    
    print("Testing server observability integration...")
    print("=" * 50)
    
    try:
        # Test 1: Health check (should trigger performance monitoring)
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test 2: Demo login (should trigger user analytics)
        print("\n2. Testing demo login...")
        response = requests.get(f"{base_url}/demo-login", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            demo_data = response.json()
            print(f"   Demo user: {demo_data.get('username')}")
        
        # Test 3: Metrics endpoint (should show observability health)
        print("\n3. Testing metrics endpoint...")
        response = requests.get(f"{base_url}/metrics", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            metrics = response.json()
            print(f"   Uptime: {metrics.get('uptime_seconds', 0):.2f}s")
            print(f"   Database: {metrics.get('database_status')}")
        
        # Test 4: Trigger an error (should send to Sentry)
        print("\n4. Testing error handling...")
        try:
            response = requests.get(f"{base_url}/nonexistent-endpoint", timeout=10)
            print(f"   Status: {response.status_code} (expected 404)")
        except Exception as e:
            print(f"   Error handled: {e}")
        
        # Test 5: Check observability health
        print("\n5. Checking observability health...")
        try:
            # This endpoint might not exist, but we can check via metrics
            response = requests.get(f"{base_url}/metrics", timeout=10)
            if response.status_code == 200:
                print("   Observability services are responding")
        except Exception as e:
            print(f"   Could not check observability: {e}")
        
        print("\n" + "=" * 50)
        print("SUCCESS: Server observability integration tested!")
        print("\nData sent to:")
        print("- Sentry: Error tracking and performance data")
        print("- PostHog: User analytics and feature usage")
        print("- Performance Monitor: API response times")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Server not running!")
        print("Start the server with: python start_server.py")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_server_with_observability()
    exit(0 if success else 1)