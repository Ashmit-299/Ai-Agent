#!/usr/bin/env python3
"""
Debug Server Issues - Simple Version
"""
import os
import sys
import traceback

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    
    try:
        import fastapi
        print("SUCCESS: FastAPI imported")
    except Exception as e:
        print(f"ERROR: FastAPI import failed - {e}")
        return False
    
    try:
        import uvicorn
        print("SUCCESS: Uvicorn imported")
    except Exception as e:
        print(f"ERROR: Uvicorn import failed - {e}")
        return False
    
    return True

def test_main_app():
    """Test main app import"""
    print("\nTesting main app...")
    
    try:
        from app.main import app
        print("SUCCESS: Main app imported")
        
        # Check routes
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        print(f"Found {len(routes)} routes")
        if routes:
            print("Sample routes:", routes[:3])
            return True
        else:
            print("ERROR: No routes found")
            return False
            
    except Exception as e:
        print(f"ERROR: Main app import failed - {e}")
        print("Full error:")
        traceback.print_exc()
        return False

def test_simple_server():
    """Test simple server start"""
    print("\nTesting simple server...")
    
    try:
        from fastapi import FastAPI
        import uvicorn
        
        # Create simple app
        simple_app = FastAPI()
        
        @simple_app.get("/")
        def root():
            return {"message": "Simple server working"}
        
        @simple_app.get("/health")
        def health():
            return {"status": "ok"}
        
        print("SUCCESS: Simple app created with routes")
        
        # Test if we can create server config
        config = uvicorn.Config(
            app=simple_app,
            host="127.0.0.1", 
            port=9001,  # Different port
            log_level="info"
        )
        
        print("SUCCESS: Server config created")
        print("Simple server should work on port 9001")
        return True
        
    except Exception as e:
        print(f"ERROR: Simple server test failed - {e}")
        traceback.print_exc()
        return False

def check_port():
    """Check if port is available"""
    print("\nChecking port 9000...")
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9000))
        sock.close()
        
        if result == 0:
            print("ERROR: Port 9000 is in use")
            return False
        else:
            print("SUCCESS: Port 9000 is available")
            return True
    except Exception as e:
        print(f"ERROR: Port check failed - {e}")
        return False

def start_minimal_server():
    """Start a minimal working server"""
    print("\nStarting minimal server test...")
    
    try:
        from fastapi import FastAPI
        
        app = FastAPI(title="Minimal Test Server")
        
        @app.get("/")
        def root():
            return {
                "message": "Minimal server is working",
                "status": "success",
                "endpoints": ["/", "/health", "/test"]
            }
        
        @app.get("/health")
        def health():
            return {"status": "healthy", "server": "minimal"}
        
        @app.get("/test")
        def test():
            return {"test": "working", "timestamp": "now"}
        
        print("SUCCESS: Minimal server created")
        print("Routes available:")
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                print(f"  {list(route.methods)[0] if route.methods else 'GET'} {route.path}")
        
        return app
        
    except Exception as e:
        print(f"ERROR: Minimal server creation failed - {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("SERVER DEBUG")
    print("=" * 40)
    
    # Run tests
    import_ok = test_imports()
    port_ok = check_port()
    simple_ok = test_simple_server()
    
    print("\n" + "=" * 40)
    print("MAIN APP TEST")
    print("=" * 40)
    
    main_ok = test_main_app()
    
    print("\n" + "=" * 40)
    print("SUMMARY")
    print("=" * 40)
    
    if import_ok and port_ok and simple_ok:
        print("Basic server components: WORKING")
    else:
        print("Basic server components: FAILED")
    
    if main_ok:
        print("Main app: WORKING")
        print("\nTry starting server with:")
        print("python -m uvicorn app.main:app --host 127.0.0.1 --port 9000")
    else:
        print("Main app: FAILED")
        print("\nTry minimal server:")
        print("python -c \"from debug_server import start_minimal_server; import uvicorn; app=start_minimal_server(); uvicorn.run(app, host='127.0.0.1', port=9001)\"")
    
    print("=" * 40)