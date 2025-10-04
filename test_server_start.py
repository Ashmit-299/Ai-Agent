#!/usr/bin/env python3
"""
Quick test script to verify the FastAPI server starts correctly
"""

import sys
import os
import time

def test_server_startup():
    """Test if the server can start without errors"""
    print("Testing FastAPI server startup...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Test imports
        print("Testing imports...")
        from app.main import app
        print("FastAPI app imported successfully")
        
        # Test basic app configuration
        print("Testing app configuration...")
        print(f"   Title: {app.title}")
        print(f"   Version: {app.version}")
        print(f"   Routes: {len(app.routes)} endpoints")
        
        # Test OpenAPI schema generation
        print("Testing OpenAPI schema...")
        schema = app.openapi()
        print(f"   Schema paths: {len(schema.get('paths', {}))}")
        
        print("Server startup test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Server startup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_endpoints():
    """Test if basic endpoints are accessible"""
    print("\nTesting basic endpoint accessibility...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app=app)
        
        # Test health endpoint
        response = client.get("/health")
        print(f"   /health: {response.status_code}")
        
        # Test docs endpoint
        response = client.get("/docs")
        print(f"   /docs: {response.status_code}")
        
        # Test OpenAPI endpoint
        response = client.get("/openapi.json")
        print(f"   /openapi.json: {response.status_code}")
        
        print("Basic endpoints test completed!")
        return True
        
    except Exception as e:
        print(f"Basic endpoints test failed: {e}")
        return False

if __name__ == "__main__":
    print("AI-Agent FastAPI Server Test")
    print("=" * 40)
    
    startup_ok = test_server_startup()
    
    if startup_ok:
        endpoints_ok = test_basic_endpoints()
        
        if endpoints_ok:
            print("\nAll tests passed! Server should start correctly.")
            print("\nTo start the server:")
            print("   python scripts/start_server.py")
            print("   OR")
            print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 9000")
        else:
            print("\nEndpoint tests failed - check route configuration")
    else:
        print("\nStartup test failed - check imports and configuration")