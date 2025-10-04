#!/usr/bin/env python3
"""
Restart observability services with correct configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def reinitialize_observability():
    """Reinitialize observability services"""
    print("🔄 Reinitializing observability services...")
    
    try:
        # Import and reinitialize
        from app.observability import initialize_observability
        
        # Force reinitialization
        sentry_manager, posthog_manager, performance_monitor, structured_logger = initialize_observability()
        
        print(f"✅ Sentry initialized: {sentry_manager.initialized}")
        print(f"✅ PostHog initialized: {posthog_manager.initialized}")
        
        # Test both services
        if sentry_manager.initialized:
            sentry_manager.capture_message("Observability services restarted", level="info")
            print("✅ Sentry test message sent")
        
        if posthog_manager.initialized:
            posthog_manager.track_event("system", "observability_restart", {"success": True})
            print("✅ PostHog test event sent")
        
        return sentry_manager.initialized, posthog_manager.initialized
        
    except Exception as e:
        print(f"❌ Failed to reinitialize: {e}")
        return False, False

def main():
    print("🚀 Observability Services Restart")
    print("=" * 40)
    
    # Check environment variables
    sentry_dsn = os.getenv("SENTRY_DSN")
    posthog_key = os.getenv("POSTHOG_API_KEY")
    
    print(f"SENTRY_DSN: {'✅' if sentry_dsn else '❌'}")
    print(f"POSTHOG_API_KEY: {'✅' if posthog_key else '❌'}")
    
    if sentry_dsn:
        print(f"Sentry DSN: {sentry_dsn[:50]}...")
    if posthog_key:
        print(f"PostHog Key: {posthog_key[:20]}...")
    
    # Reinitialize
    sentry_ok, posthog_ok = reinitialize_observability()
    
    print("\n" + "=" * 40)
    print("📊 Results:")
    print(f"Sentry: {'✅ Active' if sentry_ok else '❌ Failed'}")
    print(f"PostHog: {'✅ Active' if posthog_ok else '❌ Failed'}")
    
    if sentry_ok or posthog_ok:
        print("\n🎉 Observability services are now active!")
        print("The /observability/health endpoint should now show enabled=true")
    else:
        print("\n⚠️  Services failed to initialize. Check your configuration.")

if __name__ == "__main__":
    main()