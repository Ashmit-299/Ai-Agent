#!/usr/bin/env python3
"""
Simple import test to verify all required packages are available
"""

import os

def test_imports():
    """Test all critical imports for the AI-Agent project"""
    results = []
    
    # Core FastAPI dependencies
    try:
        import fastapi
        results.append(("OK", "fastapi", fastapi.__version__))
    except ImportError as e:
        results.append(("FAIL", "fastapi", str(e)))
    
    try:
        import uvicorn
        results.append(("OK", "uvicorn", uvicorn.__version__))
    except ImportError as e:
        results.append(("FAIL", "uvicorn", str(e)))
    
    # Database dependencies
    try:
        import sqlmodel
        results.append(("OK", "sqlmodel", sqlmodel.__version__))
    except ImportError as e:
        results.append(("FAIL", "sqlmodel", str(e)))
    
    try:
        import alembic
        results.append(("OK", "alembic", alembic.__version__))
    except ImportError as e:
        results.append(("FAIL", "alembic", str(e)))
    
    # Authentication
    try:
        import jwt
        results.append(("OK", "PyJWT", jwt.__version__))
    except ImportError as e:
        results.append(("FAIL", "PyJWT", str(e)))
    
    try:
        import bcrypt
        results.append(("OK", "bcrypt", bcrypt.__version__))
    except ImportError as e:
        results.append(("FAIL", "bcrypt", str(e)))
    
    # Video processing
    try:
        import moviepy
        results.append(("OK", "moviepy", moviepy.__version__))
    except ImportError as e:
        results.append(("FAIL", "moviepy", str(e)))
    
    # Monitoring with connection validation
    try:
        import sentry_sdk
        from dotenv import load_dotenv
        load_dotenv()
        
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn and not sentry_dsn.startswith("your-"):
            results.append(("OK", "sentry-sdk", f"{sentry_sdk.VERSION} (configured)"))
        else:
            results.append(("WARN", "sentry-sdk", f"{sentry_sdk.VERSION} (not configured)"))
    except ImportError as e:
        results.append(("FAIL", "sentry-sdk", str(e)))
    
    try:
        import posthog
        from dotenv import load_dotenv
        load_dotenv()
        
        posthog_key = os.getenv("POSTHOG_API_KEY")
        if posthog_key and not posthog_key.startswith("your-"):
            results.append(("OK", "posthog", "installed (configured)"))
        else:
            results.append(("WARN", "posthog", "installed (not configured)"))
    except ImportError as e:
        results.append(("FAIL", "posthog", str(e)))
    
    # Dashboard
    try:
        import streamlit
        results.append(("OK", "streamlit", streamlit.__version__))
    except ImportError as e:
        results.append(("FAIL", "streamlit", str(e)))
    
    # Standard library (should always work)
    try:
        import sqlite3
        results.append(("OK", "sqlite3", "built-in"))
    except ImportError as e:
        results.append(("FAIL", "sqlite3", str(e)))
    
    # Environment file check
    try:
        from dotenv import load_dotenv
        if os.path.exists('.env'):
            results.append(("OK", ".env file", "exists"))
        else:
            results.append(("WARN", ".env file", "missing - copy from .env.example"))
    except ImportError:
        results.append(("WARN", "python-dotenv", "not installed"))
    
    return results

if __name__ == "__main__":
    print("Testing package imports for AI-Agent...")
    print("=" * 50)
    
    results = test_imports()
    success_count = 0
    
    for status, package, version in results:
        print(f"{status} {package:<15} {version}")
        if status in ["OK", "WARN"]:
            success_count += 1
    
    print("=" * 50)
    print(f"Results: {success_count}/{len(results)} packages available")
    
    warnings = [r for r in results if r[0] == "WARN"]
    failures = [r for r in results if r[0] == "FAIL"]
    
    if failures:
        print(f"ERROR: {len(failures)} packages missing. Run: pip install -r requirements.txt")
        exit(1)
    elif warnings:
        print(f"SUCCESS: All packages available, {len(warnings)} need configuration")
        print("\nConfiguration Guide:")
        for _, package, msg in warnings:
            if "sentry" in package:
                print(f"  - Sentry: Get DSN from https://sentry.io/settings/projects/")
            elif "posthog" in package:
                print(f"  - PostHog: Get API key from https://app.posthog.com/project/settings")
            elif ".env" in package:
                print(f"  - Environment: Copy .env.example to .env and fill values")
            else:
                print(f"  - {package}: {msg}")
        exit(0)
    else:
        print("SUCCESS: All packages are available and configured!")
        exit(0)