#!/usr/bin/env python3
"""
Simple integration test for Sentry and PostHog
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry():
    """Test Sentry integration"""
    try:
        import sentry_sdk
        print("[OK] Sentry SDK imported successfully")
        
        dsn = os.getenv("SENTRY_DSN")
        if dsn:
            print(f"[OK] Sentry DSN configured: {dsn[:50]}...")
            
            # Initialize Sentry
            sentry_sdk.init(dsn=dsn, environment="test")
            print("[OK] Sentry initialized successfully")
            
            # Test capture
            sentry_sdk.capture_message("Test message from integration test")
            print("[OK] Sentry test message sent")
            
            return True
        else:
            print("[ERROR] Sentry DSN not configured")
            return False
            
    except ImportError as e:
        print(f"[ERROR] Sentry SDK not available: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Sentry initialization failed: {e}")
        return False

def test_posthog():
    """Test PostHog integration"""
    try:
        from posthog import Posthog
        print("[OK] PostHog SDK imported successfully")
        
        api_key = os.getenv("POSTHOG_API_KEY")
        host = os.getenv("POSTHOG_HOST", "https://us.posthog.com")
        
        if api_key:
            print(f"[OK] PostHog API key configured: {api_key[:20]}...")
            
            # Initialize PostHog
            posthog = Posthog(project_api_key=api_key, host=host)
            print("[OK] PostHog initialized successfully")
            
            # Test capture
            posthog.capture(
                distinct_id="test-user",
                event="integration_test",
                properties={"test": True}
            )
            print("[OK] PostHog test event sent")
            
            return True
        else:
            print("[ERROR] PostHog API key not configured")
            return False
            
    except ImportError as e:
        print(f"[ERROR] PostHog SDK not available: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] PostHog initialization failed: {e}")
        return False

def test_bcrypt():
    """Test bcrypt functionality"""
    try:
        import bcrypt
        print("[OK] bcrypt imported successfully")
        
        # Test password hashing
        password = "test123"
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print("[OK] bcrypt hashing works")
        
        # Test password verification
        is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
        if is_valid:
            print("[OK] bcrypt verification works")
            return True
        else:
            print("[ERROR] bcrypt verification failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] bcrypt test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("Testing integrations...\n")
    
    results = {
        "sentry": test_sentry(),
        "posthog": test_posthog(), 
        "bcrypt": test_bcrypt()
    }
    
    print(f"\nResults:")
    for service, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {service}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)