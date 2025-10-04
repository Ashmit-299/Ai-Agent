#!/usr/bin/env python3
"""
Verify Sentry, PostHog, and Supabase integrations
"""

import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_sentry_integration():
    """Test Sentry error tracking"""
    print("Testing Sentry integration...")
    
    try:
        from app.observability import sentry_manager
        
        if not sentry_manager.initialized:
            print("[FAIL] Sentry not initialized")
            return False
        
        # Test exception capture
        try:
            raise Exception("Test exception for Sentry")
        except Exception as e:
            sentry_manager.capture_exception(e, {"test": True})
        
        # Test message capture
        sentry_manager.capture_message("Test message from integration verification", "info")
        
        print("[OK] Sentry integration working")
        return True
        
    except Exception as e:
        print(f"[FAIL] Sentry integration failed: {e}")
        return False

def test_posthog_integration():
    """Test PostHog analytics"""
    print("Testing PostHog integration...")
    
    try:
        from app.observability import posthog_manager
        
        if not posthog_manager.initialized:
            print("[FAIL] PostHog not initialized")
            return False
        
        # Test event tracking
        posthog_manager.track_event("test_user", "integration_test", {
            "test": True,
            "timestamp": time.time()
        })
        
        # Test user identification
        posthog_manager.identify_user("test_user", {
            "test_user": True,
            "integration_check": True
        })
        
        print("[OK] PostHog integration working")
        return True
        
    except Exception as e:
        print(f"[FAIL] PostHog integration failed: {e}")
        return False

def test_supabase_integration():
    """Test Supabase database connection"""
    print("Testing Supabase integration...")
    
    try:
        from core.database import DatabaseManager
        
        db = DatabaseManager()
        
        # Test basic query
        analytics_data = db.get_analytics_data()
        
        if analytics_data:
            print("[OK] Supabase integration working")
            print(f"   Users: {analytics_data.get('total_users', 0)}")
            print(f"   Content: {analytics_data.get('total_content', 0)}")
            print(f"   Feedback: {analytics_data.get('total_feedback', 0)}")
            return True
        else:
            print("[FAIL] Supabase query returned no data")
            return False
            
    except Exception as e:
        print(f"[FAIL] Supabase integration failed: {e}")
        return False

def test_endpoint_integrations():
    """Test that endpoints are properly integrated"""
    print("Testing endpoint integrations...")
    
    try:
        import requests
        
        base_url = "http://localhost:8000"
        
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("[OK] Health endpoint working")
        else:
            print(f"[FAIL] Health endpoint failed: {response.status_code}")
            return False
        
        # Test metrics endpoint
        response = requests.get(f"{base_url}/metrics", timeout=10)
        if response.status_code == 200:
            print("[OK] Metrics endpoint working")
        else:
            print(f"[FAIL] Metrics endpoint failed: {response.status_code}")
        
        # Test observability health
        response = requests.get(f"{base_url}/observability/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("[OK] Observability health endpoint working")
            print(f"   Sentry enabled: {data.get('observability_health', {}).get('sentry', {}).get('enabled', False)}")
            print(f"   PostHog enabled: {data.get('observability_health', {}).get('posthog', {}).get('enabled', False)}")
        else:
            print(f"[FAIL] Observability health endpoint failed: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Endpoint integration test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("=== Integration Verification ===")
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    results = {
        "sentry": test_sentry_integration(),
        "posthog": test_posthog_integration(), 
        "supabase": test_supabase_integration(),
        "endpoints": test_endpoint_integrations()
    }
    
    print()
    print("=== Results Summary ===")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for service, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{service.upper()}: {status}")
    
    print()
    print(f"Overall: {passed_tests}/{total_tests} integrations working")
    
    if passed_tests == total_tests:
        print("[SUCCESS] All integrations verified successfully!")
    else:
        print("[WARNING] Some integrations need attention")
    
    # Save results
    report = {
        "timestamp": time.time(),
        "results": results,
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests
        }
    }
    
    try:
        os.makedirs("data/reports", exist_ok=True)
        with open("data/reports/integration_verification.json", "w") as f:
            json.dump(report, f, indent=2)
        print("[SAVED] Report saved to data/reports/integration_verification.json")
    except Exception as e:
        print(f"Failed to save report: {e}")

if __name__ == "__main__":
    main()