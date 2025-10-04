#!/usr/bin/env python3
"""
Simple integration check for PostHog, Sentry, and Supabase
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_sentry():
    """Check Sentry configuration and availability"""
    print("Checking Sentry Integration...")
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        print("ERROR: SENTRY_DSN not configured in .env")
        return False
    
    print(f"OK: SENTRY_DSN configured: {sentry_dsn[:50]}...")
    
    try:
        import sentry_sdk
        print("OK: Sentry SDK installed")
        return True
    except ImportError:
        print("ERROR: Sentry SDK not installed")
        return False

def check_posthog():
    """Check PostHog configuration and availability"""
    print("\nChecking PostHog Integration...")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    host = os.getenv("POSTHOG_HOST", "https://us.posthog.com")
    
    if not api_key:
        print("ERROR: POSTHOG_API_KEY not configured in .env")
        return False
    
    print(f"OK: POSTHOG_API_KEY configured: {api_key[:20]}...")
    print(f"OK: POSTHOG_HOST: {host}")
    
    try:
        from posthog import Posthog
        print("OK: PostHog SDK installed")
        return True
    except ImportError:
        print("ERROR: PostHog SDK not installed")
        return False

def check_supabase():
    """Check Supabase configuration and availability"""
    print("\nChecking Supabase Integration...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    if not url or not key:
        print("ERROR: SUPABASE_URL or SUPABASE_ANON_KEY not configured")
        return False
    
    print(f"OK: SUPABASE_URL: {url}")
    print(f"OK: SUPABASE_ANON_KEY configured: {key[:20]}...")
    
    if database_url and "supabase" in database_url:
        print("OK: DATABASE_URL configured for Supabase")
    
    try:
        import psycopg2
        print("OK: psycopg2 installed for database connection")
    except ImportError:
        print("WARNING: psycopg2 not installed")
    
    try:
        from supabase import create_client
        print("OK: Supabase SDK installed")
        return True
    except ImportError:
        print("ERROR: Supabase SDK not installed")
        return False

def check_observability():
    """Check observability module"""
    print("\nChecking Observability Module...")
    
    try:
        from app.observability import sentry_manager, posthog_manager
        print("OK: Observability module imported")
        print(f"Sentry manager initialized: {sentry_manager.initialized}")
        print(f"PostHog manager initialized: {posthog_manager.initialized}")
        return True
    except ImportError as e:
        print(f"ERROR: Observability module import failed: {e}")
        return False

def main():
    """Run all checks"""
    print("AI Agent Integration Status Check")
    print("=" * 40)
    
    results = {
        "Sentry": check_sentry(),
        "PostHog": check_posthog(),
        "Supabase": check_supabase(),
        "Observability": check_observability()
    }
    
    print("\nSummary:")
    print("=" * 40)
    
    for service, status in results.items():
        status_text = "WORKING" if status else "NEEDS ATTENTION"
        print(f"{service}: {status_text}")
    
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nOverall: {working_count}/{total_count} integrations working")
    
    if working_count == total_count:
        print("All integrations are properly configured!")
    else:
        print("Some integrations need attention.")
    
    return 0 if working_count == total_count else 1

if __name__ == "__main__":
    exit(main())