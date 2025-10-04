#!/usr/bin/env python3
"""Verify all endpoints are working correctly"""

import requests
import json
import time

BASE_URL = "https://ai-agent-aff6.onrender.com"

def test_endpoint(endpoint, expected_status=200, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        status_ok = response.status_code == expected_status
        print(f"{'OK' if status_ok else 'FAIL'} {method} {endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                if endpoint == "/metrics":
                    metrics = data.get('system_metrics', {})
                    print(f"   Users: {metrics.get('total_users', 0)}, Content: {metrics.get('total_contents', 0)}, Feedback: {metrics.get('total_feedback', 0)}")
                elif endpoint == "/contents":
                    items = data.get('items', [])
                    print(f"   Found {len(items)} content items")
                elif endpoint == "/bhiv/analytics":
                    print(f"   Users: {data.get('total_users', 0)}, Content: {data.get('total_content', 0)}")
            except:
                pass
        
        return status_ok
    except Exception as e:
        print(f"FAIL {method} {endpoint}: ERROR - {e}")
        return False

def verify_all():
    """Test all key endpoints"""
    print("Verifying all endpoints...")
    
    # Wait for deployment
    print("Waiting 2 minutes for deployment...")
    time.sleep(120)
    
    endpoints = [
        "/health",
        "/demo-login", 
        "/contents",
        "/metrics",
        "/bhiv/analytics",
        "/rl/agent-stats",
        "/bucket/stats",
        "/streaming-performance",
        "/dashboard"
    ]
    
    results = {}
    for endpoint in endpoints:
        results[endpoint] = test_endpoint(endpoint)
    
    print(f"\nResults: {sum(results.values())}/{len(results)} endpoints working")
    
    # Test specific metrics values
    print("\nTesting metrics values...")
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=30)
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('system_metrics', {})
            
            if metrics.get('total_contents', 0) > 0:
                print("OK: Metrics showing real content data")
            else:
                print("FAIL: Metrics still showing zero content")
                
            if metrics.get('total_users', 0) > 0:
                print("OK: Metrics showing real user data")
            else:
                print("FAIL: Metrics still showing zero users")
    except Exception as e:
        print(f"FAIL: Metrics test failed: {e}")

if __name__ == "__main__":
    verify_all()