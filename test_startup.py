#!/usr/bin/env python3
"""
Test application startup to verify all integrations
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_startup():
    """Test application startup components"""
    print("Testing application startup components...\n")
    
    # Test environment variables
    print("1. Environment Variables:")
    env_vars = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "SENTRY_DSN": os.getenv("SENTRY_DSN"),
        "POSTHOG_API_KEY": os.getenv("POSTHOG_API_KEY")
    }
    
    for key, value in env_vars.items():
        status = "[OK]" if value else "[MISSING]"
        display_value = f"{value[:30]}..." if value and len(value) > 30 else value or "Not set"
        print(f"   {key}: {status} {display_value}")
    
    # Test imports
    print("\n2. Module Imports:")
    modules_to_test = [
        ("sentry_sdk", "Sentry SDK"),
        ("posthog", "PostHog SDK"),
        ("bcrypt", "bcrypt"),
        ("fastapi", "FastAPI"),
        ("sqlmodel", "SQLModel"),
        ("core.database", "Database module"),
        ("app.observability", "Observability module")
    ]
    
    import_results = {}
    for module_name, display_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"   {display_name}: [OK]")
            import_results[module_name] = True
        except ImportError as e:
            print(f"   {display_name}: [ERROR] {e}")
            import_results[module_name] = False
    
    # Test observability initialization
    print("\n3. Observability Services:")
    if import_results.get("app.observability"):
        try:
            from app.observability import sentry_manager, posthog_manager
            print(f"   Sentry initialized: [{'OK' if sentry_manager.initialized else 'FAILED'}]")
            print(f"   PostHog initialized: [{'OK' if posthog_manager.initialized else 'FAILED'}]")
        except Exception as e:
            print(f"   Observability test: [ERROR] {e}")
    
    # Test database connection
    print("\n4. Database Connection:")
    try:
        from core.database import get_session
        with get_session() as session:
            # Simple test query
            result = session.execute("SELECT 1 as test")
            if result.fetchone():
                print("   Database connection: [OK]")
            else:
                print("   Database connection: [FAILED]")
    except Exception as e:
        print(f"   Database connection: [ERROR] {e}")
    
    print("\n5. Configuration Validation:")
    try:
        from app.config import validate_config
        if validate_config():
            print("   Configuration: [OK]")
        else:
            print("   Configuration: [INCOMPLETE]")
    except Exception as e:
        print(f"   Configuration: [ERROR] {e}")
    
    print("\nStartup test completed!")

if __name__ == "__main__":
    test_startup()