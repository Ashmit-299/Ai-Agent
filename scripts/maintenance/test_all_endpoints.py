#!/usr/bin/env python3
"""
Test all endpoints with observability integration
"""

import requests
import json
import time
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

BASE_URL = "http://localhost:8000"

def get_demo_token():
    """Get demo user token for authenticated requests"""
    try:
        # Get demo credentials
        response = requests.get(f"{BASE_URL}/demo-login", timeout=10)
        if response.status_code != 200:
            return None
        
        demo_data = response.json()
        username = demo_data["demo_credentials"]["username"]
        password = demo_data["demo_credentials"]["password"]
        
        # Login to get token
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}/users/login", data=login_data, timeout=10)
        if response.status_code == 200:
            return response.json()["access_token"]
        
        return None
        
    except Exception as e:
        print(f"Failed to get demo token: {e}")
        return None

def test_endpoint(method, path, headers=None, data=None, files=None):
    """Test a single endpoint"""
    try:
        url = f"{BASE_URL}{path}"
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, files=files, timeout=10)
        else:
            return {"status": "unsupported_method", "method": method}
        
        return {
            "status": "success" if response.status_code < 400 else "error",
            "status_code": response.status_code,
            "response_time_ms": response.elapsed.total_seconds() * 1000,
            "content_length": len(response.content) if response.content else 0
        }
        
    except Exception as e:
        return {
            "status": "exception",
            "error": str(e)
        }

def main():
    """Test all endpoints"""
    print("=== Testing All Endpoints with Observability ===")
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get authentication token
    token = get_demo_token()
    auth_headers = {"Authorization": f"Bearer {token}"} if token else None
    
    if token:
        print("[OK] Authentication token obtained")
    else:
        print("[FAIL] Failed to get authentication token")
    
    print()
    
    # Define endpoints to test
    endpoints = [
        # Public endpoints
        {"method": "GET", "path": "/", "name": "Root"},
        {"method": "GET", "path": "/health", "name": "Health Check"},
        {"method": "GET", "path": "/demo-login", "name": "Demo Login"},
        {"method": "GET", "path": "/test", "name": "Simple Test"},
        
        # Authentication endpoints
        {"method": "GET", "path": "/debug-auth", "name": "Debug Auth", "auth": True},
        {"method": "GET", "path": "/users/profile", "name": "User Profile", "auth": True},
        
        # Content endpoints
        {"method": "GET", "path": "/contents", "name": "List Contents"},
        
        # Analytics endpoints
        {"method": "GET", "path": "/metrics", "name": "System Metrics"},
        {"method": "GET", "path": "/bhiv/analytics", "name": "BHIV Analytics"},
        {"method": "GET", "path": "/observability/health", "name": "Observability Health"},
        {"method": "GET", "path": "/observability/performance", "name": "Performance Metrics"},
        
        # Task queue endpoints
        {"method": "GET", "path": "/tasks/queue/stats", "name": "Queue Stats"},
        
        # Dashboard
        {"method": "GET", "path": "/dashboard", "name": "Dashboard"},
        
        # Bucket stats
        {"method": "GET", "path": "/bucket/stats", "name": "Bucket Stats"},
    ]
    
    results = {}
    total_endpoints = len(endpoints)
    successful_endpoints = 0
    
    for endpoint in endpoints:
        method = endpoint["method"]
        path = endpoint["path"]
        name = endpoint["name"]
        requires_auth = endpoint.get("auth", False)
        
        headers = auth_headers if requires_auth else None
        
        print(f"Testing {name} ({method} {path})...")
        
        result = test_endpoint(method, path, headers)
        results[path] = result
        
        if result["status"] == "success":
            successful_endpoints += 1
            status_icon = "[OK]"
        else:
            status_icon = "[FAIL]"
        
        print(f"  {status_icon} {result.get('status_code', 'N/A')} - {result.get('response_time_ms', 0):.0f}ms")
        
        if result["status"] == "exception":
            print(f"     Error: {result['error']}")
    
    print()
    print("=== Results Summary ===")
    print(f"Total endpoints tested: {total_endpoints}")
    print(f"Successful responses: {successful_endpoints}")
    print(f"Success rate: {(successful_endpoints/total_endpoints)*100:.1f}%")
    
    # Show slow endpoints
    slow_endpoints = []
    for path, result in results.items():
        if result.get("response_time_ms", 0) > 1000:
            slow_endpoints.append((path, result["response_time_ms"]))
    
    if slow_endpoints:
        print()
        print("[WARNING] Slow endpoints (>1s):")
        for path, time_ms in sorted(slow_endpoints, key=lambda x: x[1], reverse=True):
            print(f"  {path}: {time_ms:.0f}ms")
    
    # Test observability integration
    print()
    print("=== Testing Observability Integration ===")
    
    try:
        from app.observability import sentry_manager, posthog_manager
        
        print(f"Sentry initialized: {'[OK]' if sentry_manager.initialized else '[FAIL]'}")
        print(f"PostHog initialized: {'[OK]' if posthog_manager.initialized else '[FAIL]'}")
        
        # Test tracking
        if posthog_manager.initialized:
            posthog_manager.track_event("test_user", "endpoint_test_completed", {
                "total_endpoints": total_endpoints,
                "successful_endpoints": successful_endpoints,
                "test_timestamp": time.time()
            })
            print("[OK] PostHog event tracked")
        
        if sentry_manager.initialized:
            sentry_manager.capture_message("Endpoint testing completed", "info", {
                "total_endpoints": total_endpoints,
                "successful_endpoints": successful_endpoints
            })
            print("[OK] Sentry message sent")
            
    except Exception as e:
        print(f"[FAIL] Observability test failed: {e}")
    
    # Save results
    report = {
        "timestamp": time.time(),
        "base_url": BASE_URL,
        "total_endpoints": total_endpoints,
        "successful_endpoints": successful_endpoints,
        "success_rate": (successful_endpoints/total_endpoints)*100,
        "results": results,
        "slow_endpoints": slow_endpoints
    }
    
    try:
        os.makedirs("data/reports", exist_ok=True)
        with open("data/reports/endpoint_test_results.json", "w") as f:
            json.dump(report, f, indent=2)
        print("[SAVED] Results saved to data/reports/endpoint_test_results.json")
    except Exception as e:
        print(f"Failed to save results: {e}")

if __name__ == "__main__":
    main()