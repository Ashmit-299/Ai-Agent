#!/usr/bin/env python3
"""
Test script to check PostHog, Sentry, and Supabase integrations
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sentry_integration():
    """Test Sentry integration"""
    print("Testing Sentry Integration...")
    
    sentry_dsn = os.getenv("SENTRY_DSN")
    if not sentry_dsn:
        print("❌ SENTRY_DSN not configured in .env")
        return False
    
    print(f"✅ SENTRY_DSN configured: {sentry_dsn[:50]}...")
    
    try:
        import sentry_sdk
        print("✅ Sentry SDK installed")
        
        # Test initialization
        sentry_sdk.init(dsn=sentry_dsn, traces_sample_rate=0.1)
        print("✅ Sentry initialized successfully")
        
        # Test capture
        sentry_sdk.capture_message("Integration test message", level="info")
        print("✅ Sentry message captured")
        
        return True
    except ImportError:
        print("❌ Sentry SDK not installed (pip install sentry-sdk)")
        return False
    except Exception as e:
        print(f"❌ Sentry error: {e}")
        return False

def test_posthog_integration():
    """Test PostHog integration"""
    print("\nTesting PostHog Integration...")
    
    api_key = os.getenv("POSTHOG_API_KEY")
    host = os.getenv("POSTHOG_HOST", "https://us.posthog.com")
    
    if not api_key:
        print("❌ POSTHOG_API_KEY not configured in .env")
        return False
    
    print(f"✅ POSTHOG_API_KEY configured: {api_key[:20]}...")
    print(f"✅ POSTHOG_HOST: {host}")
    
    try:
        from posthog import Posthog
        print("✅ PostHog SDK installed")
        
        # Test initialization
        client = Posthog(project_api_key=api_key, host=host)
        print("✅ PostHog client initialized")
        
        # Test event capture
        client.capture(
            distinct_id="test-integration",
            event="integration_test",
            properties={"source": "test_script"}
        )
        print("✅ PostHog event captured")
        
        return True
    except ImportError:
        print("❌ PostHog SDK not installed (pip install posthog)")
        return False
    except Exception as e:
        print(f"❌ PostHog error: {e}")
        return False

def test_supabase_integration():
    """Test Supabase integration"""
    print("\nTesting Supabase Integration...")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    if not url or not key:
        print("❌ SUPABASE_URL or SUPABASE_ANON_KEY not configured")
        return False
    
    print(f"✅ SUPABASE_URL: {url}")
    print(f"✅ SUPABASE_ANON_KEY configured: {key[:20]}...")
    
    # Test database connection
    if database_url and "supabase" in database_url:
        print(f"✅ DATABASE_URL configured for Supabase")
        
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            print(f"✅ Database connection successful: {version[:50]}...")
            cur.close()
            conn.close()
            
        except ImportError:
            print("❌ psycopg2 not installed (pip install psycopg2-binary)")
            return False
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    # Test Supabase client
    try:
        from supabase import create_client
        print("✅ Supabase SDK installed")
        
        client = create_client(url, key)
        print("✅ Supabase client initialized")
        
        # Test storage
        try:
            buckets = client.storage.list_buckets()
            print(f"✅ Storage accessible, found {len(buckets)} buckets")
        except Exception as storage_error:
            print(f"⚠️ Storage test failed: {storage_error}")
        
        return True
    except ImportError:
        print("❌ Supabase SDK not installed (pip install supabase)")
        return False
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        return False

def test_observability_module():
    """Test the observability module"""
    print("\nTesting Observability Module...")
    
    try:
        from app.observability import sentry_manager, posthog_manager, get_observability_health
        print("✅ Observability module imported successfully")
        
        # Test health check
        health = get_observability_health()
        print(f"✅ Observability health: {health}")
        
        # Test managers
        print(f"✅ Sentry manager initialized: {sentry_manager.initialized}")
        print(f"✅ PostHog manager initialized: {posthog_manager.initialized}")
        
        return True
    except ImportError as e:
        print(f"❌ Observability module import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Observability module error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("AI Agent Integration Test Suite")
    print("=" * 50)
    
    results = {
        "sentry": test_sentry_integration(),
        "posthog": test_posthog_integration(), 
        "supabase": test_supabase_integration(),
        "observability": test_observability_module()
    }
    
    print("\nIntegration Test Results:")
    print("=" * 50)
    
    for service, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {service.upper()}: {'WORKING' if status else 'FAILED'}")
    
    working_count = sum(results.values())
    total_count = len(results)
    
    print(f"\nOverall Status: {working_count}/{total_count} integrations working")
    
    if working_count == total_count:
        print("All integrations are working properly!")
        return 0
    else:
        print("Some integrations need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())