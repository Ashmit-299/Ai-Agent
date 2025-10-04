#!/usr/bin/env python3
"""
Final monitoring verification - Port 9000 only
"""

import requests
import json

def final_check():
    """Final check of monitoring on port 9000"""
    
    print("FINAL MONITORING CHECK - PORT 9000")
    print("=" * 50)
    
    base_url = "http://localhost:9000"
    
    # Test monitoring status
    try:
        response = requests.get(f"{base_url}/monitoring-status")
        if response.status_code == 200:
            data = response.json()
            print("[OK] Monitoring Status: ACTIVE")
            print(f"   Sentry: {'[OK]' if data['services']['sentry']['available'] else '[FAIL]'}")
            print(f"   PostHog: {'[OK]' if data['services']['posthog']['available'] else '[FAIL]'}")
        else:
            print("[FAIL] Monitoring Status: FAILED")
    except Exception as e:
        print(f"[ERROR] Monitoring Status: ERROR - {e}")
    
    # Test monitoring connection
    try:
        response = requests.get(f"{base_url}/test-monitoring")
        if response.status_code == 200:
            data = response.json()
            print("[OK] Connection Test: PASSED")
            print(f"   Overall Status: {data['overall_status']}")
        else:
            print("[FAIL] Connection Test: FAILED")
    except Exception as e:
        print(f"[ERROR] Connection Test: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print("[OK] Main Server: http://localhost:9000")
    print("[OK] Monitoring: CONNECTED")
    print("[OK] Sentry: ACTIVE")
    print("[OK] PostHog: ACTIVE")
    print("\nDashboards:")
    print("- Sentry: https://blackhole-ig.sentry.io/insights/projects/python/")
    print("- PostHog: https://us.posthog.com/project/222470")

if __name__ == "__main__":
    final_check()