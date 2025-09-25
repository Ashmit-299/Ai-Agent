#!/usr/bin/env python3
"""Check actual connection status"""

import os
import time
from dotenv import load_dotenv

load_dotenv()

def check_sentry_real_connection():
    """Test real Sentry connection"""
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        dsn = os.getenv('SENTRY_DSN')
        print(f"Sentry DSN: {dsn}")
        
        # Initialize with real DSN
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=False
        )
        
        # Send test event
        event_id = sentry_sdk.capture_message("Real connection test from AI Agent", level="info")
        print(f"Sentry event sent: {event_id}")
        
        # Force flush
        sentry_sdk.flush(timeout=5)
        print("✅ Sentry CONNECTED and working")
        return True
        
    except Exception as e:
        print(f"❌ Sentry connection failed: {e}")
        return False

def check_posthog_real_connection():
    """Test real PostHog connection"""
    try:
        import posthog
        
        api_key = os.getenv('POSTHOG_API_KEY')
        host = os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
        
        print(f"PostHog API Key: {api_key[:20]}...")
        print(f"PostHog Host: {host}")
        
        # Configure PostHog
        posthog.project_api_key = api_key
        posthog.host = host
        posthog.debug = True
        
        # Send test event
        posthog.capture(
            distinct_id='connection-test-user',
            event='real_connection_test',
            properties={
                'source': 'ai_agent_verification',
                'timestamp': time.time(),
                'test_type': 'connection_verification'
            }
        )
        
        # Identify user
        posthog.identify(
            distinct_id='connection-test-user',
            properties={
                'email': 'test@aiagent.com',
                'connection_test': True
            }
        )
        
        print("✅ PostHog CONNECTED and working")
        return True
        
    except Exception as e:
        print(f"❌ PostHog connection failed: {e}")
        return False

def main():
    print("REAL CONNECTION STATUS CHECK")
    print("=" * 40)
    
    sentry_ok = check_sentry_real_connection()
    print()
    posthog_ok = check_posthog_real_connection()
    
    print("\n" + "=" * 40)
    print("FINAL STATUS:")
    print(f"Sentry: {'CONNECTED' if sentry_ok else 'DISCONNECTED'}")
    print(f"PostHog: {'CONNECTED' if posthog_ok else 'DISCONNECTED'}")
    
    if sentry_ok and posthog_ok:
        print("\n🎉 BOTH SERVICES CONNECTED!")
        print("Check your dashboards:")
        print("- Sentry: https://sentry.io")
        print("- PostHog: https://app.posthog.com")
    else:
        print("\n⚠️ Connection issues detected")

if __name__ == "__main__":
    main()