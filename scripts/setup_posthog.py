#!/usr/bin/env python3
"""
PostHog Analytics Setup Guide for AI Agent
"""

import os
import posthog

def setup_posthog():
    """Setup PostHog analytics"""
    
    # Get API key from environment
    api_key = os.getenv("POSTHOG_API_KEY")
    
    if not api_key:
        print("[X] POSTHOG_API_KEY not found in environment variables")
        print("\nSetup Steps:")
        print("1. Go to https://posthog.com and create account")
        print("2. Create new project")
        print("3. Copy your Project API Key")
        print("4. Add to .env file: POSTHOG_API_KEY=phc_your_key_here")
        return False
    
    # Initialize PostHog
    posthog.api_key = api_key
    posthog.host = 'https://app.posthog.com'
    
    # Test connection
    try:
        posthog.capture(
            distinct_id='setup_test',
            event='posthog_setup_test',
            properties={'source': 'setup_script'}
        )
        print("[OK] PostHog connected successfully!")
        print(f"API Key: {api_key[:10]}...")
        print("Dashboard: https://app.posthog.com")
        return True
    except Exception as e:
        print(f"[ERROR] PostHog connection failed: {e}")
        return False

if __name__ == "__main__":
    setup_posthog()