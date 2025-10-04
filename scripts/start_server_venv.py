#!/usr/bin/env python3
"""
Server startup script with dependency checking and async verification
"""
import os
import sys
import subprocess
import asyncio

def check_dependencies():
    """Check critical dependencies"""
    print("🔍 Checking dependencies...")
    
    required = ['fastapi', 'uvicorn', 'httpx', 'tenacity', 'sqlmodel', 'vaderSentiment', 'python-jose', 'passlib', 'bcrypt']
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            missing.append(module)
            print(f"  ❌ {module}")
    
    if missing:
        print(f"\n❌ Missing: {', '.join(missing)}")
        print("Installing missing dependencies...")
        venv_pip = os.path.join('venv', 'Scripts', 'pip.exe')
        if os.path.exists(venv_pip):
            subprocess.run([venv_pip, 'install'] + missing)
        else:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing)
    
    return True

async def test_async_functionality():
    """Test Day 1 async implementation"""
    print("\n🧪 Testing async functionality...")
    
    try:
        sys.path.append('.')
        
        # Test core async functions
        from core import bhiv_core
        result = await bhiv_core.process_script_upload_async(
            script_text="Test script",
            uploader="startup_test"
        )
        print(f"  ✅ Async core: {result['status']}")
        
        # Test LM client
        from core import bhiv_lm_client
        result = await bhiv_lm_client.suggest_storyboard("Test")
        print(f"  ✅ LM client: {result.get('generation_method', 'working')}")
        
        # Test database
        from ..core.database import DatabaseManager
        db = DatabaseManager()
        analytics = db.get_analytics_data()
        print(f"  ✅ Database: {len(analytics)} metrics")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Async test failed: {e}")
        return False

def main():
    """Start the server using virtual environment"""
    print("🎯 AI Content Uploader Agent - Enhanced Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("❌ Error: app/main.py not found. Run from project root.")
        sys.exit(1)
    
    # Check if virtual environment exists
    if not os.path.exists('venv/Scripts/activate.bat'):
        print("❌ Error: Virtual environment not found. Create it first.")
        sys.exit(1)
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('bucket/tmp', exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Test imports
    print("\n📦 Testing imports...")
    try:
        sys.path.append('.')
        from ..app.main import app
        from ..app.routes import router
        print(f"  ✅ FastAPI app ({len(router.routes)} endpoints)")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        sys.exit(1)
    
    # Test async functionality
    try:
        success = asyncio.run(test_async_functionality())
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Async test error: {e}")
        sys.exit(1)
    
    print("\n✅ All systems ready!")
    
    try:
        # Use virtual environment Python to run the server
        venv_python = os.path.join('venv', 'Scripts', 'python.exe')
        
        if not os.path.exists(venv_python):
            print("❌ Error: Virtual environment Python not found.")
            sys.exit(1)
        
        # Run the application with virtual environment
        cmd = [venv_python, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
        
        print("\n🚀 Starting server...")
        print(f"🌐 Server: http://localhost:8000")
        print(f"📚 API docs: http://localhost:8000/docs")
        print(f"🔍 Health: http://localhost:8000/health")
        print(f"🎬 Demo: http://localhost:8000/demo-login")
        print("\nPress Ctrl+C to stop")
        print("=" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()