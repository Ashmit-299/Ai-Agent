#!/usr/bin/env python3
"""
Test script to verify PostHog and Sentry integration
"""

import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

def test_observability():
    """Test PostHog and Sentry integration"""
    
    print("🔍 Testing Observability Integration...")
    
    # Check environment variables
    sentry_dsn = os.getenv("SENTRY_DSN")
    posthog_key = os.getenv("POSTHOG_API_KEY")
    
    print(f"Sentry DSN configured: {'✅' if sentry_dsn and not sentry_dsn.startswith('your-') else '❌'}")
    print(f"PostHog API Key configured: {'✅' if posthog_key and not posthog_key.startswith('your-') else '❌'}")
    
    # Test server health
    try:
        response = requests.get("http://localhost:8000/health/detailed", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print("\n📊 Observability Health:")
            
            sentry_status = health_data.get("observability", {}).get("sentry", {})
            posthog_status = health_data.get("observability", {}).get("posthog", {})
            
            print(f"Sentry enabled: {'✅' if sentry_status.get('enabled') else '❌'}")
            print(f"PostHog enabled: {'✅' if posthog_status.get('enabled') else '❌'}")
            
        else:
            print("❌ Server health check failed")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: python scripts/start_server.py")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test error tracking (Sentry)
    try:
        print("\n🚨 Testing error tracking...")
        response = requests.post("http://localhost:8000/test-error", timeout=5)
        print("✅ Error tracking test sent")
    except:
        print("ℹ️  Error tracking test endpoint not available")
    
    # Test event tracking (PostHog)
    try:
        print("\n📈 Testing event tracking...")
        # This would be done through your app's endpoints
        response = requests.get("http://localhost:8000/demo-login", timeout=5)
        if response.status_code == 200:
            print("✅ Event tracking test completed")
    except Exception as e:
        print(f"❌ Event tracking test failed: {e}")
    
    print("\n🎉 Observability test completed!")
    print("\nNext steps:")
    print("1. Check your Sentry dashboard for errors")
    print("2. Check your PostHog dashboard for events")
    print("3. Monitor real user interactions")
    
    return True

if __name__ == "__main__":
    test_observability()