#!/usr/bin/env python3
"""
Test script to verify PostHog and Sentry integration
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry():
    """Test Sentry error tracking"""
    print("\nTesting Sentry Integration...")
    
    try:
        import sentry_sdk
        from app.observability import sentry_manager
        
        # Check if Sentry is configured
        sentry_dsn = os.getenv('SENTRY_DSN')
        if not sentry_dsn or sentry_dsn == 'your-sentry-dsn':
            print("[SKIP] Sentry DSN not configured (using placeholder)")
            return False
            
        # Check if Sentry is initialized
        if not sentry_manager.initialized:
            print("[ERROR] Sentry manager not initialized")
            return False
        
        # Test Sentry capture
        print("Sending test message to Sentry...")
        sentry_manager.capture_message("Test message from AI Agent - Sentry is working!", level="info")
        
        # Test error capture
        try:
            raise Exception("Test exception for Sentry verification")
        except Exception as e:
            sentry_manager.capture_exception(e)
            print("Sent test exception to Sentry")
        
        print("[OK] Sentry integration working")
        return True
        
    except ImportError:
        print("[ERROR] Sentry SDK not installed")
        return False
    except Exception as e:
        print(f"[ERROR] Sentry error: {e}")
        return False

def test_posthog():
    """Test PostHog analytics"""
    print("\nTesting PostHog Integration...")
    
    try:
        from app.observability import posthog_manager
        
        # Check if PostHog is configured
        posthog_key = os.getenv('POSTHOG_API_KEY')
        if not posthog_key or posthog_key == 'your-posthog-key':
            print("[SKIP] PostHog API key not configured (using placeholder)")
            return False
            
        # Check if PostHog is initialized
        if not posthog_manager.initialized:
            print("[ERROR] PostHog manager not initialized")
            return False
        
        # Test event tracking
        print("Sending test event to PostHog...")
        posthog_manager.track_event(
            user_id='test-user-123',
            event='test_event',
            properties={
                'test_property': 'verification_test',
                'source': 'ai_agent_test'
            }
        )
        
        # Test user identification
        posthog_manager.identify_user(
            user_id='test-user-123',
            traits={
                'email': 'test@example.com',
                'name': 'Test User',
                'test_verification': True
            }
        )
        
        print("[OK] PostHog integration working")
        return True
        
    except ImportError:
        print("[ERROR] PostHog SDK not installed")
        return False
    except Exception as e:
        print(f"[ERROR] PostHog error: {e}")
        return False

def test_observability_in_app():
    """Test observability integration in FastAPI app"""
    print("\nTesting Observability in FastAPI App...")
    
    try:
        from app.observability import get_observability_health, performance_monitor
        
        # Test health check
        health = get_observability_health()
        print(f"Observability health: {health}")
        
        # Test performance monitor
        with performance_monitor.measure_operation("test_operation"):
            time.sleep(0.1)  # Simulate work
        
        print("[OK] Observability components working")
        return True
        
    except Exception as e:
        print(f"[ERROR] App integration error: {e}")
        return False

def test_environment_config():
    """Test environment configuration"""
    print("\nTesting Environment Configuration...")
    
    # Check required environment variables
    required_vars = {
        'SENTRY_DSN': os.getenv('SENTRY_DSN'),
        'POSTHOG_API_KEY': os.getenv('POSTHOG_API_KEY'),
        'POSTHOG_HOST': os.getenv('POSTHOG_HOST', 'https://app.posthog.com')
    }
    
    all_configured = True
    for var, value in required_vars.items():
        if not value or value.startswith('your-'):
            print(f"[SKIP] {var}: Not configured (placeholder value)")
            all_configured = False
        else:
            print(f"[OK] {var}: Configured")
    
    return all_configured

def main():
    """Run all observability tests"""
    print("AI Agent Observability Verification")
    print("=" * 50)
    
    results = {
        'environment': test_environment_config(),
        'sentry': test_sentry(),
        'posthog': test_posthog(),
        'app_integration': test_observability_in_app()
    }
    
    print("\nTest Results Summary:")
    print("=" * 30)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("All observability services are working correctly!")
        print("Check your Sentry and PostHog dashboards for test data")
    else:
        print("Some observability services need configuration")
        print("Update your .env file with valid API keys")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)