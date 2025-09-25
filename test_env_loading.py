#!/usr/bin/env python3
"""Test environment variable loading"""

import os
from dotenv import load_dotenv

print("Testing environment loading...")

# Load .env file
load_dotenv()

# Check key variables
sentry_dsn = os.getenv('SENTRY_DSN')
posthog_key = os.getenv('POSTHOG_API_KEY')
posthog_host = os.getenv('POSTHOG_HOST')

print(f"Sentry DSN: {sentry_dsn[:50]}..." if sentry_dsn else "Sentry DSN: Not loaded")
print(f"PostHog Key: {posthog_key[:20]}..." if posthog_key else "PostHog Key: Not loaded")
print(f"PostHog Host: {posthog_host}")

# Test actual integration
try:
    from app.observability import sentry_manager, posthog_manager
    print(f"Sentry initialized: {sentry_manager.initialized}")
    print(f"PostHog initialized: {posthog_manager.initialized}")
    
    if sentry_manager.initialized:
        print("✅ Sending test to Sentry...")
        sentry_manager.capture_message("Environment test - Sentry working!")
    
    if posthog_manager.initialized:
        print("✅ Sending test to PostHog...")
        posthog_manager.track_event("test-user", "env_test", {"source": "env_verification"})
        
except Exception as e:
    print(f"Error: {e}")