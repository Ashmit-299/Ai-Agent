#!/usr/bin/env python3
"""
Quick test to verify endpoints work after RLS fixes
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """Test basic endpoints without auth"""
    
    print("Testing basic endpoints...")
    
    # Test health
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Health: {response.status_code}")
    except:
        print("Server not running. Start with: uvicorn app.main:app --reload")
        return False
    
    # Test demo login
    try:
        response = requests.get(f"{BASE_URL}/demo-login")
        print(f"Demo login: {response.status_code}")
    except Exception as e:
        print(f"Demo login failed: {e}")
    
    # Test contents list
    try:
        response = requests.get(f"{BASE_URL}/contents")
        print(f"Contents list: {response.status_code}")
    except Exception as e:
        print(f"Contents failed: {e}")
    
    # Test metrics
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        print(f"Metrics: {response.status_code}")
    except Exception as e:
        print(f"Metrics failed: {e}")
    
    # Test analytics summary
    try:
        response = requests.get(f"{BASE_URL}/analytics/summary")
        print(f"Analytics summary: {response.status_code}")
    except Exception as e:
        print(f"Analytics failed: {e}")
    
    print("Basic tests completed!")
    return True

if __name__ == "__main__":
    print("Quick API Test After RLS Fix")
    print("=" * 30)
    test_basic_endpoints()