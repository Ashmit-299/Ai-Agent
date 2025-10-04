#!/usr/bin/env python3
"""
Fix observability services initialization
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment variables are properly set"""
    print("🔍 Checking environment variables...")
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    posthog_key = os.getenv("POSTHOG_API_KEY")
    
    print(f"SENTRY_DSN: {'✅ Set' if sentry_dsn else '❌ Not set'}")
    if sentry_dsn:
        print(f"  Value: {sentry_dsn[:50]}...")
    
    print(f"POSTHOG_API_KEY: {'✅ Set' if posthog_key else '❌ Not set'}")
    if posthog_key:
        print(f"  Value: {posthog_key[:20]}...")
    
    return bool(sentry_dsn), bool(posthog_key)

def test_sentry_initialization():
    """Test Sentry initialization"""
    print("\n🔧 Testing Sentry initialization...")
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        print("✅ Sentry SDK imported successfully")
        
        sentry_dsn = os.getenv("SENTRY_DSN")
        if not sentry_dsn:
            print("❌ SENTRY_DSN not configured")
            return False
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=os.getenv("ENVIRONMENT", "development"),
            integrations=[FastApiIntegration()],
            traces_sample_rate=1.0,
            send_default_pii=False
        )
        
        # Test by sending a message
        sentry_sdk.capture_message("Test message from fix_observability.py", level="info")
        print("✅ Sentry initialized and test message sent")
        return True
        
    except ImportError as e:
        print(f"❌ Sentry SDK not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Sentry initialization failed: {e}")
        return False

def test_posthog_initialization():
    """Test PostHog initialization"""
    print("\n🔧 Testing PostHog initialization...")
    
    try:
        from posthog import Posthog
        print("✅ PostHog SDK imported successfully")
        
        posthog_key = os.getenv("POSTHOG_API_KEY")
        if not posthog_key:
            print("❌ POSTHOG_API_KEY not configured")
            return False
        
        # Initialize PostHog
        posthog = Posthog(
            project_api_key=posthog_key,
            host=os.getenv("POSTHOG_HOST", "https://us.posthog.com"),
            debug=True
        )
        
        # Test by sending an event
        posthog.capture(
            distinct_id="test-user",
            event="test_event_from_fix_script",
            properties={"source": "fix_observability.py"}
        )
        print("✅ PostHog initialized and test event sent")
        return True
        
    except ImportError as e:
        print(f"❌ PostHog SDK not available: {e}")
        return False
    except Exception as e:
        print(f"❌ PostHog initialization failed: {e}")
        return False

def test_observability_endpoint():
    """Test the observability health endpoint"""
    print("\n🔧 Testing observability health endpoint...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:9000/observability/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Observability health endpoint accessible")
            print(f"Sentry enabled: {data['observability_health']['sentry']['enabled']}")
            print(f"PostHog enabled: {data['observability_health']['posthog']['enabled']}")
            return data
        else:
            print(f"❌ Health endpoint returned status {response.status_code}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 9000")
        return None
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return None

def main():
    print("🚀 Observability Services Fix Script")
    print("=" * 50)
    
    # Check environment
    sentry_configured, posthog_configured = check_environment()
    
    if not sentry_configured and not posthog_configured:
        print("\n❌ No observability services configured!")
        print("Please set SENTRY_DSN and/or POSTHOG_API_KEY in your .env file")
        return
    
    # Test individual services
    sentry_working = test_sentry_initialization() if sentry_configured else False
    posthog_working = test_posthog_initialization() if posthog_configured else False
    
    # Test endpoint
    endpoint_data = test_observability_endpoint()
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"Sentry: {'✅ Working' if sentry_working else '❌ Failed'}")
    print(f"PostHog: {'✅ Working' if posthog_working else '❌ Failed'}")
    
    if endpoint_data:
        endpoint_sentry = endpoint_data['observability_health']['sentry']['enabled']
        endpoint_posthog = endpoint_data['observability_health']['posthog']['enabled']
        print(f"Endpoint reports - Sentry: {'✅' if endpoint_sentry else '❌'}, PostHog: {'✅' if endpoint_posthog else '❌'}")
    
    if sentry_working or posthog_working:
        print("\n🎉 At least one observability service is working!")
        print("Restart your server to apply the fixes.")
    else:
        print("\n⚠️  No observability services are working.")
        print("Check your environment variables and network connectivity.")

if __name__ == "__main__":
    main()