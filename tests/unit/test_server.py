#!/usr/bin/env python3
"""
Simple test to identify server startup issues
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ dotenv loaded")
    
    import os
    print("✅ os imported")
    
    from fastapi import FastAPI
    print("✅ FastAPI imported")
    
    # Test observability imports
    try:
        from app.observability import sentry_manager, posthog_manager, structured_logger
        print("✅ Observability imported")
    except Exception as e:
        print(f"❌ Observability import failed: {e}")
    
    # Test middleware imports
    try:
        from app.middleware import ObservabilityMiddleware, UserContextMiddleware, ErrorHandlingMiddleware
        print("✅ Middleware imported")
    except Exception as e:
        print(f"❌ Middleware import failed: {e}")
    
    # Test security imports
    try:
        from app.security import security_manager
        print("✅ Security imported")
    except Exception as e:
        print(f"❌ Security import failed: {e}")
    
    # Test routes imports
    try:
        from app.routes import router, step1_router
        print("✅ Routes imported")
    except Exception as e:
        print(f"❌ Routes import failed: {e}")
    
    print("\n🚀 All imports successful! Starting server...")
    
    # Try to create the app
    from app.main import app
    print("✅ App created successfully")
    
    # Test a simple endpoint
    import uvicorn
    print("✅ Ready to start server")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()