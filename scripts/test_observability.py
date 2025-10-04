#!/usr/bin/env python3
"""
Test observability services (Sentry and PostHog) configuration
"""

import os
import sys
sys.path.append('.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from app.observability import sentry_manager, posthog_manager, get_observability_health
import json

def test_observability():
    """Test observability services configuration"""
    
    print("Testing Observability Services Configuration")
    print("=" * 50)
    
    # Check environment variables
    print("\nEnvironment Variables:")
    print(f"SENTRY_DSN: {'Set' if os.getenv('SENTRY_DSN') else 'Not set'}")
    print(f"POSTHOG_API_KEY: {'Set' if os.getenv('POSTHOG_API_KEY') else 'Not set'}")
    print(f"POSTHOG_HOST: {os.getenv('POSTHOG_HOST', 'Not set')}")
    print(f"ENVIRONMENT: {os.getenv('ENVIRONMENT', 'Not set')}")
    
    # Test Sentry
    print(f"\nSentry Status:")
    print(f"Initialized: {'Yes' if sentry_manager.initialized else 'No'}")
    if sentry_manager.initialized:
        try:
            sentry_manager.capture_message("Test message from observability test", "info")
            print("Test message sent successfully")
        except Exception as e:
            print(f"Failed to send test message: {e}")
    
    # Test PostHog
    print(f"\nPostHog Status:")
    print(f"Initialized: {'Yes' if posthog_manager.initialized else 'No'}")
    if posthog_manager.initialized:
        try:
            posthog_manager.track_event("test_user", "observability_test", {"test": True})
            print("Test event sent successfully")
        except Exception as e:
            print(f"Failed to send test event: {e}")
    
    # Get health status
    print(f"\nHealth Status:")
    health = get_observability_health()
    print(json.dumps(health, indent=2))
    
    # Recommendations
    print(f"\nRecommendations:")
    if not sentry_manager.initialized:
        print("- Set SENTRY_DSN in .env file")
        print("- Ensure Sentry DSN format: https://xxx@xxx.ingest.sentry.io/xxx")
    
    if not posthog_manager.initialized:
        print("- Set POSTHOG_API_KEY in .env file")
        print("- Ensure PostHog API key format: phc_xxx")
        print("- Set POSTHOG_HOST (default: https://us.posthog.com)")

if __name__ == "__main__":
    test_observability()