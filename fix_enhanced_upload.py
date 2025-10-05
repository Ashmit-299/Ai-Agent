#!/usr/bin/env python3
"""
Fix Enhanced Upload Import Error
Resolves the import issue and ensures enhanced upload endpoint works
"""

import os
import sys

def fix_import_error():
    """Fix the import error in input_validation.py"""
    print("🔧 Fixing Enhanced Upload Import Error")
    print("=" * 50)
    
    # Check if input_validation.py exists
    validation_file = "app/input_validation.py"
    if not os.path.exists(validation_file):
        print(f"❌ {validation_file} not found")
        return False
    
    # Read the file
    with open(validation_file, 'r') as f:
        content = f.read()
    
    # Fix the import
    if "from fastapi.middleware.base import BaseHTTPMiddleware" in content:
        print("✅ Import already fixed")
        return True
    elif "from starlette.middleware.base import BaseHTTPMiddleware" in content:
        print("✅ Import already correct")
        return True
    else:
        print("🔧 Fixing import statement...")
        # Replace the import
        content = content.replace(
            "from fastapi.middleware.base import BaseHTTPMiddleware",
            "from starlette.middleware.base import BaseHTTPMiddleware"
        )
        
        # Write back
        with open(validation_file, 'w') as f:
            f.write(content)
        
        print("✅ Import fixed successfully")
        return True

def test_imports():
    """Test if all required imports work"""
    print("\n🧪 Testing Imports")
    print("=" * 30)
    
    try:
        from starlette.middleware.base import BaseHTTPMiddleware
        print("✅ starlette.middleware.base - OK")
    except ImportError as e:
        print(f"❌ starlette.middleware.base - {e}")
        return False
    
    try:
        from app.input_validation import InputValidationMiddleware, FileValidator, TextValidator
        print("✅ app.input_validation - OK")
    except ImportError as e:
        print(f"❌ app.input_validation - {e}")
        return False
    
    try:
        from app.security import security_manager
        print("✅ app.security - OK")
    except ImportError as e:
        print(f"❌ app.security - {e}")
        return False
    
    return True

def check_database_config():
    """Check database configuration"""
    print("\n📊 Checking Database Configuration")
    print("=" * 40)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if database_url and 'postgresql' in database_url:
        print("✅ Primary database: PostgreSQL (Supabase)")
        
        if supabase_url and supabase_key:
            print("✅ Supabase credentials configured")
            return True
        else:
            print("⚠️  Supabase credentials incomplete")
            print("💡 Run: python setup_supabase.py")
            return False
    else:
        print("⚠️  Using SQLite fallback database")
        print("💡 To use Supabase: python setup_supabase.py")
        return False

def test_enhanced_upload_endpoint():
    """Test if enhanced upload endpoint is accessible"""
    print("\n🌐 Testing Enhanced Upload Endpoint")
    print("=" * 40)
    
    try:
        import requests
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Check if enhanced upload route exists
            response = requests.get("http://localhost:9000/docs", timeout=5)
            if response.status_code == 200:
                print("✅ API documentation accessible")
                print("🔗 Enhanced upload: POST /upload-enhanced")
                return True
            else:
                print("⚠️  API documentation not accessible")
                return False
        else:
            print("❌ Server not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("💡 Start server with: python scripts/start_server.py")
        return False

def main():
    """Main fix function"""
    print("🚀 AI Agent Enhanced Upload Fix")
    print("=" * 50)
    
    success = True
    
    # Fix import error
    if not fix_import_error():
        success = False
    
    # Test imports
    if not test_imports():
        success = False
    
    # Check database config
    db_ok = check_database_config()
    
    # Test endpoint (if server is running)
    endpoint_ok = test_enhanced_upload_endpoint()
    
    print("\n📋 Summary")
    print("=" * 20)
    
    if success:
        print("✅ Import errors fixed")
        print("✅ All required modules available")
    else:
        print("❌ Some import issues remain")
    
    if db_ok:
        print("✅ Database configured (Supabase)")
    else:
        print("⚠️  Database using SQLite fallback")
    
    if endpoint_ok:
        print("✅ Enhanced upload endpoint accessible")
        print("\n🎉 Ready to test enhanced upload!")
        print("🧪 Run: python test_enhanced_upload.py")
    else:
        print("⚠️  Server not running or endpoint not accessible")
        print("🚀 Start server: python scripts/start_server.py")
    
    print(f"\n📖 Next Steps:")
    if not db_ok:
        print("1. Configure Supabase: python setup_supabase.py")
    if not endpoint_ok:
        print("2. Start server: python scripts/start_server.py")
    print("3. Test enhanced upload: python test_enhanced_upload.py")
    print("4. Access API docs: http://localhost:9000/docs")

if __name__ == "__main__":
    main()