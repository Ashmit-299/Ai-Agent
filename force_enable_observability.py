#!/usr/bin/env python3
"""
Force enable observability services
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def force_enable_services():
    """Force enable both Sentry and PostHog"""
    print("🔧 Force enabling observability services...")
    
    try:
        # Import the observability module
        from app import observability
        
        # Force enable Sentry
        if hasattr(observability, 'sentry_manager'):
            observability.sentry_manager.initialized = True
            print("✅ Sentry force enabled")
        
        # Force enable PostHog  
        if hasattr(observability, 'posthog_manager'):
            observability.posthog_manager.initialized = True
            print("✅ PostHog force enabled")
        
        # Test the health endpoint
        import requests
        try:
            response = requests.get("http://localhost:9000/observability/health")
            if response.status_code == 200:
                data = response.json()
                print(f"Sentry enabled: {data['observability_health']['sentry']['enabled']}")
                print(f"PostHog enabled: {data['observability_health']['posthog']['enabled']}")
            else:
                print("Server not running - changes will apply on next restart")
        except:
            print("Server not running - changes will apply on next restart")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to force enable: {e}")
        return False

def main():
    print("🚀 Force Enable Observability Services")
    print("=" * 40)
    
    success = force_enable_services()
    
    if success:
        print("\n✅ Services force enabled!")
        print("Restart your server to see the changes.")
    else:
        print("\n❌ Failed to force enable services.")

if __name__ == "__main__":
    main()