#!/usr/bin/env python3
"""
Quick health check for CI/CD pipelines
"""

import sys
import requests
import time

def quick_health_check(api_url, timeout=30):
    """Quick health check for essential endpoints"""
    
    essential_endpoints = [
        "/health",
        "/docs", 
        "/demo-login"
    ]
    
    print(f"[QUICK] Health check for {api_url}")
    
    failed = 0
    total = len(essential_endpoints)
    
    for endpoint in essential_endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{api_url}{endpoint}", timeout=timeout)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"[OK] {endpoint} - {duration:.0f}ms")
            else:
                print(f"[ERROR] {endpoint} - Status: {response.status_code}")
                failed += 1
                
        except Exception as e:
            print(f"[ERROR] {endpoint} - {str(e)}")
            failed += 1
    
    success_rate = ((total - failed) / total) * 100
    
    print(f"\n[RESULT] {total - failed}/{total} checks passed ({success_rate:.0f}%)")
    
    if failed == 0:
        print("[STATUS] HEALTHY")
        return True
    else:
        print("[STATUS] UNHEALTHY")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python quick-health-check.py <API_URL>")
        sys.exit(1)
    
    api_url = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    success = quick_health_check(api_url, timeout)
    sys.exit(0 if success else 1)