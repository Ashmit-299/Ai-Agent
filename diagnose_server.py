#!/usr/bin/env python3
"""
Diagnose Server Issues
"""
import os
import sys
import traceback
from dotenv import load_dotenv

load_dotenv()

def test_basic_imports():
    """Test if basic imports work"""
    print("Testing basic imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the FastAPI app can be created"""
    print("\nTesting app creation...")
    
    try:
        from fastapi import FastAPI
        app = FastAPI()
        print("✅ Basic FastAPI app created")
        return True
    except Exception as e:
        print(f"❌ Basic app creation failed: {e}")
        traceback.print_exc()
        return False

def test_main_app_import():
    """Test importing the main app"""
    print("\nTesting main app import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        from app.main import app
        print("✅ Main app imported successfully")
        
        # Check if app has routes
        routes = [route.path for route in app.routes]
        print(f"✅ Found {len(routes)} routes")
        
        # Show first few routes
        if routes:
            print("Sample routes:", routes[:5])
        else:
            print("❌ No routes found!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        traceback.print_exc()
        return False

def test_server_start():
    """Test if server can start"""
    print("\nTesting server startup...")
    
    try:
        import uvicorn
        from app.main import app
        
        # Test server configuration
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=9000,
            log_level="info"
        )
        
        print("✅ Server config created")
        print("Server should be able to start on http://127.0.0.1:9000")
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        traceback.print_exc()
        return False

def check_port_availability():
    """Check if port 9000 is available"""
    print("\nChecking port availability...")
    
    import socket
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9000))
        sock.close()
        
        if result == 0:
            print("❌ Port 9000 is already in use!")
            print("Kill existing server or use different port")
            return False
        else:
            print("✅ Port 9000 is available")
            return True
            
    except Exception as e:
        print(f"❌ Port check failed: {e}")
        return False

def test_simple_endpoint():
    """Test creating a simple endpoint"""
    print("\nTesting simple endpoint creation...")
    
    try:
        from fastapi import FastAPI
        
        test_app = FastAPI()
        
        @test_app.get("/test")
        def test_endpoint():
            return {"message": "test working"}
        
        # Check if route was added
        routes = [route.path for route in test_app.routes]
        if "/test" in routes:
            print("✅ Simple endpoint created successfully")
            return True
        else:
            print("❌ Endpoint not found in routes")
            return False
            
    except Exception as e:
        print(f"❌ Simple endpoint test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("SERVER DIAGNOSIS")
    print("=" * 50)
    
    tests = [
        test_basic_imports,
        test_app_creation,
        test_simple_endpoint,
        check_port_availability,
        test_main_app_import,
        test_server_start
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
        print("-" * 30)
    
    print("\nDIAGNOSIS SUMMARY:")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed - server should work")
        print("\nTry starting with:")
        print("python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload")
    else:
        print("❌ Some tests failed - check errors above")
        print("\nFailed tests:")
        for i, (test, result) in enumerate(zip(tests, results)):
            if not result:
                print(f"- {test.__name__}")
    
    print("=" * 50)