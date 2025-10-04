#!/usr/bin/env python3
"""
Test live connections to PostHog, Sentry, and Supabase
"""

import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_live():
    """Test live Sentry connection"""
    print("Testing live Sentry connection...")
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            traces_sample_rate=0.1,
            integrations=[LoggingIntegration(level=None, event_level=None)]
        )
        
        # Send test message
        sentry_sdk.capture_message("Integration test from AI Agent", level="info")
        print("OK: Test message sent to Sentry")
        
        # Send test exception
        try:
            raise Exception("Test exception for integration check")
        except Exception as e:
            sentry_sdk.capture_exception(e)
            print("OK: Test exception sent to Sentry")
        
        return True
    except Exception as e:
        print(f"ERROR: Sentry live test failed: {e}")
        return False

def test_posthog_live():
    """Test live PostHog connection"""
    print("\nTesting live PostHog connection...")
    
    try:
        from posthog import Posthog
        
        # Initialize PostHog
        client = Posthog(
            project_api_key=os.getenv("POSTHOG_API_KEY"),
            host=os.getenv("POSTHOG_HOST", "https://us.posthog.com")
        )
        
        # Send test event
        client.capture(
            distinct_id="integration-test-user",
            event="integration_test",
            properties={
                "source": "live_test",
                "timestamp": time.time(),
                "test_type": "connection_check"
            }
        )
        print("OK: Test event sent to PostHog")
        
        # Send identify event
        client.identify(
            distinct_id="integration-test-user",
            properties={
                "test_user": True,
                "integration_check": True
            }
        )
        print("OK: User identification sent to PostHog")
        
        return True
    except Exception as e:
        print(f"ERROR: PostHog live test failed: {e}")
        return False

def test_supabase_live():
    """Test live Supabase connection"""
    print("\nTesting live Supabase connection...")
    
    try:
        # Test database connection
        import psycopg2
        database_url = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        # Test basic query
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"OK: Database connected - {version[:50]}...")
        
        # Test table existence
        cur.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        print(f"OK: Found {len(tables)} tables in database")
        
        cur.close()
        conn.close()
        
        # Test Supabase client
        from supabase import create_client
        
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_ANON_KEY")
        )
        
        # Test storage
        try:
            buckets = client.storage.list_buckets()
            print(f"OK: Storage accessible - {len(buckets)} buckets found")
        except Exception as storage_error:
            print(f"WARNING: Storage test failed: {storage_error}")
        
        return True
    except Exception as e:
        print(f"ERROR: Supabase live test failed: {e}")
        return False

def test_observability_live():
    """Test live observability system"""
    print("\nTesting live observability system...")
    
    try:
        from app.observability import (
            sentry_manager, posthog_manager, 
            capture_exception, track_event,
            get_observability_health
        )
        
        # Test health check
        health = get_observability_health()
        print(f"OK: Health check - Sentry: {health['sentry']['enabled']}, PostHog: {health['posthog']['enabled']}")
        
        # Test exception capture
        try:
            raise ValueError("Test exception for observability")
        except Exception as e:
            capture_exception(e, {"test": "live_integration"})
            print("OK: Exception captured through observability system")
        
        # Test event tracking
        track_event("test-user", "integration_test", {
            "test_type": "live_observability",
            "timestamp": time.time()
        })
        print("OK: Event tracked through observability system")
        
        return True
    except Exception as e:
        print(f"ERROR: Observability live test failed: {e}")
        return False

def main():
    """Run all live connection tests"""
    print("AI Agent Live Integration Test")
    print("=" * 40)
    
    results = {
        "Sentry Live": test_sentry_live(),
        "PostHog Live": test_posthog_live(),
        "Supabase Live": test_supabase_live(),
        "Observability Live": test_observability_live()
    }
    
    print("\nLive Test Results:")
    print("=" * 40)
    
    for service, status in results.items():
        status_text = "CONNECTED" if status else "FAILED"
        print(f"{service}: {status_text}")
    
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nOverall: {working_count}/{total_count} live connections working")
    
    if working_count == total_count:
        print("All integrations are working properly with live connections!")
    else:
        print("Some integrations have connection issues.")
    
    return 0 if working_count == total_count else 1

if __name__ == "__main__":
    exit(main())