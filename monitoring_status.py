#!/usr/bin/env python3
"""
Monitoring status endpoint for AI-Agent
"""

import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def get_monitoring_status():
    """Get current monitoring service status"""
    
    # Check Sentry configuration
    sentry_dsn = os.getenv("SENTRY_DSN")
    sentry_configured = bool(sentry_dsn and not sentry_dsn.startswith("your-"))
    
    # Check PostHog configuration  
    posthog_key = os.getenv("POSTHOG_API_KEY")
    posthog_configured = bool(posthog_key and not posthog_key.startswith("your-"))
    
    # Import status
    try:
        import sentry_sdk
        sentry_available = True
        sentry_version = sentry_sdk.VERSION
    except ImportError:
        sentry_available = False
        sentry_version = "not installed"
    
    try:
        import posthog
        posthog_available = True
        posthog_version = "installed"
    except ImportError:
        posthog_available = False
        posthog_version = "not installed"
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "sentry": {
                "available": sentry_available,
                "configured": sentry_configured,
                "version": sentry_version,
                "status": "active" if (sentry_available and sentry_configured) else "inactive",
                "dashboard_url": "https://sentry.io/organizations/your-org/projects/" if sentry_configured else None
            },
            "posthog": {
                "available": posthog_available,
                "configured": posthog_configured,
                "version": posthog_version,
                "status": "active" if (posthog_available and posthog_configured) else "inactive",
                "dashboard_url": "https://app.posthog.com/" if posthog_configured else None
            }
        },
        "overall_status": "healthy" if (sentry_configured and posthog_configured) else "partial"
    }

if __name__ == "__main__":
    import json
    status = get_monitoring_status()
    print(json.dumps(status, indent=2))