#!/usr/bin/env python3
"""
Test actual connections to Sentry and PostHog services
"""

import os
from dotenv import load_dotenv
load_dotenv()

def test_sentry_connection():
    """Test Sentry connection and error reporting"""
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        dsn = os.getenv("SENTRY_DSN")
        if not dsn or dsn.startswith("your-"):
            return False, "DSN not configured"
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=dsn,
            environment="test",
            traces_sample_rate=0.1
        )
        
        # Test error capture
        try:
            sentry_sdk.capture_message("Test connection from AI-Agent", level="info")
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Failed to send test message: {e}"
            
    except ImportError:
        return False, "sentry-sdk not installed"
    except Exception as e:
        return False, f"Connection failed: {e}"

def test_posthog_connection():
    """Test PostHog connection and event tracking"""
    try:
        from posthog import Posthog
        
        api_key = os.getenv("POSTHOG_API_KEY")
        host = os.getenv("POSTHOG_HOST", "https://us.posthog.com")
        
        if not api_key or api_key.startswith("your-"):
            return False, "API key not configured"
        
        # Initialize PostHog
        posthog = Posthog(
            project_api_key=api_key,
            host=host,
            debug=True
        )
        
        # Test event tracking
        try:
            posthog.capture(
                distinct_id="test-user-ai-agent",
                event="connection_test",
                properties={
                    "source": "ai-agent",
                    "test": True
                }
            )
            posthog.shutdown()
            return True, "Connected successfully"
        except Exception as e:
            return False, f"Failed to send test event: {e}"
            
    except ImportError:
        return False, "posthog not installed"
    except Exception as e:
        return False, f"Connection failed: {e}"

def main():
    print("Testing monitoring service connections...")
    print("=" * 50)
    
    # Test Sentry
    sentry_success, sentry_msg = test_sentry_connection()
    status = "OK" if sentry_success else "FAIL"
    print(f"{status} Sentry        {sentry_msg}")
    
    # Test PostHog
    posthog_success, posthog_msg = test_posthog_connection()
    status = "OK" if posthog_success else "FAIL"
    print(f"{status} PostHog       {posthog_msg}")
    
    print("=" * 50)
    
    if sentry_success and posthog_success:
        print("SUCCESS: Both monitoring services are connected!")
        print("\nNext steps:")
        print("- Check Sentry dashboard for the test message")
        print("- Check PostHog dashboard for the test event")
        return True
    else:
        print("CONFIGURATION NEEDED:")
        if not sentry_success:
            print("\nSentry Setup:")
            print("1. Go to https://sentry.io/")
            print("2. Create account/login")
            print("3. Create new project (Python/FastAPI)")
            print("4. Copy DSN to .env file as SENTRY_DSN=...")
        
        if not posthog_success:
            print("\nPostHog Setup:")
            print("1. Go to https://app.posthog.com/")
            print("2. Create account/login")
            print("3. Go to Project Settings")
            print("4. Copy API key to .env file as POSTHOG_API_KEY=...")
        
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)