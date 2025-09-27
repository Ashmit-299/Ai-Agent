#!/usr/bin/env python3
"""
Quick test to verify backend can start without errors
"""

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        from app.main import app
        print("✅ FastAPI app import successful")
    except Exception as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    try:
        from core.database_integration import db_integration
        print("✅ Database integration import successful")
    except Exception as e:
        print(f"⚠️  Database integration import failed: {e}")
        print("   This is expected if tables don't exist yet")
    
    try:
        from core.database import DatabaseManager
        print("✅ Database manager import successful")
    except Exception as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic app functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test root endpoint
        response = client.get("/")
        if response.status_code in [200, 307]:  # 307 is redirect
            print("✅ Root endpoint working")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def main():
    print("🚀 Testing AI-Agent Backend Startup")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Functionality tests failed")
        return False
    
    print("\n✅ All tests passed!")
    print("🎉 Backend should start successfully")
    print("\nTo start the server:")
    print("  uvicorn app.main:app --reload")
    print("  or")
    print("  python scripts/start_server.py")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)