#!/usr/bin/env python3
"""
Test Supabase JWKS integration
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_jwks_module():
    """Test JWKS module import and configuration"""
    print("Testing JWKS Module...")
    
    try:
        from app.jwks_auth import (
            supabase_jwks_auth, 
            get_supabase_auth_health,
            SUPABASE_URL,
            JWKS_URL
        )
        print("OK: JWKS module imported successfully")
        
        # Test configuration
        print(f"Supabase URL: {SUPABASE_URL}")
        print(f"JWKS URL: {JWKS_URL}")
        
        # Test health check
        health = get_supabase_auth_health()
        print(f"JWKS Health: {health}")
        
        # Test JWKS fetch
        if SUPABASE_URL:
            jwks = supabase_jwks_auth.get_jwks()
            if jwks:
                print("OK: JWKS fetched successfully")
                print(f"JWKS keys count: {len(jwks.get('keys', []))}")
            else:
                print("WARNING: JWKS fetch returned None")
        else:
            print("INFO: SUPABASE_URL not configured, skipping JWKS fetch")
        
        return True
    except Exception as e:
        print(f"ERROR: JWKS module test failed: {e}")
        return False

async def test_enhanced_auth():
    """Test enhanced authentication system"""
    print("\nTesting Enhanced Authentication...")
    
    try:
        from app.auth import (
            get_current_user_required,
            get_current_user_optional,
            get_current_user_required_supabase,
            get_current_user_optional_supabase
        )
        print("OK: Enhanced auth functions imported")
        
        # Test security manager integration
        from app.security import JWTManager
        print("OK: Enhanced JWTManager available")
        
        # Test token verification (will fail without valid token, but should not crash)
        try:
            test_token = "invalid_token"
            JWTManager.verify_token(test_token)
        except Exception as e:
            print(f"Expected: Token verification failed for invalid token: {type(e).__name__}")
        
        return True
    except Exception as e:
        print(f"ERROR: Enhanced auth test failed: {e}")
        return False

async def test_main_integration():
    """Test main app integration"""
    print("\nTesting Main App Integration...")
    
    try:
        from app.main import app
        print("OK: Main app imported with JWKS integration")
        
        # Check if routes are available
        route_paths = [route.path for route in app.routes if hasattr(route, 'path')]
        
        auth_routes = [path for path in route_paths if 'auth' in path.lower() or 'user' in path.lower()]
        print(f"Auth-related routes found: {len(auth_routes)}")
        
        # Check for new endpoints
        if "/users/supabase-auth-health" in route_paths:
            print("OK: Supabase auth health endpoint available")
        
        return True
    except Exception as e:
        print(f"ERROR: Main app integration test failed: {e}")
        return False

async def test_dependencies():
    """Test required dependencies"""
    print("\nTesting Dependencies...")
    
    dependencies = [
        ("httpx", "HTTP client for JWKS"),
        ("jose", "JWT library"),
        ("fastapi", "Web framework"),
        ("pydantic", "Data validation")
    ]
    
    all_good = True
    for dep, desc in dependencies:
        try:
            __import__(dep)
            print(f"OK: {dep} - {desc}")
        except ImportError:
            print(f"ERROR: {dep} not available - {desc}")
            all_good = False
    
    return all_good

async def main():
    """Run all tests"""
    print("Supabase JWKS Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Dependencies", test_dependencies()),
        ("JWKS Module", test_jwks_module()),
        ("Enhanced Auth", test_enhanced_auth()),
        ("Main Integration", test_main_integration())
    ]
    
    results = {}
    for test_name, test_coro in tests:
        try:
            result = await test_coro
            results[test_name] = result
        except Exception as e:
            print(f"ERROR: {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\nTest Results:")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("All JWKS integration tests passed!")
        return 0
    else:
        print("Some tests failed - check configuration")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))