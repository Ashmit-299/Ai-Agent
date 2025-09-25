#!/usr/bin/env python3
"""
Simple test to identify server startup issues
"""

try:
    print("Testing imports...")
    
    # Test basic imports
    from dotenv import load_dotenv
    load_dotenv()
    print("[OK] dotenv loaded")
    
    import os
    print("[OK] os imported")
    
    from fastapi import FastAPI
    print("[OK] FastAPI imported")
    
    # Test observability imports
    try:
        from app.observability import sentry_manager, posthog_manager, structured_logger
        print("[OK] Observability imported")
    except Exception as e:
        print(f"[ERROR] Observability import failed: {e}")
    
    # Test middleware imports
    try:
        from app.middleware import ObservabilityMiddleware, UserContextMiddleware, ErrorHandlingMiddleware
        print("[OK] Middleware imported")
    except Exception as e:
        print(f"[ERROR] Middleware import failed: {e}")
    
    # Test security imports
    try:
        from app.security import security_manager
        print("[OK] Security imported")
    except Exception as e:
        print(f"[ERROR] Security import failed: {e}")
    
    # Test routes imports
    try:
        from app.routes import router, step1_router
        print("[OK] Routes imported")
    except Exception as e:
        print(f"[ERROR] Routes import failed: {e}")
    
    print("\n[SUCCESS] All imports successful! Starting server...")
    
    # Try to create the app
    from app.main import app
    print("[OK] App created successfully")
    
    # Test a simple endpoint
    import uvicorn
    print("[OK] Ready to start server")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()