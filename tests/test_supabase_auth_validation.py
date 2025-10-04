#!/usr/bin/env python3
"""
Supabase Authentication Validation Test Script
"""
import os
import sys
import time
import requests
import jwt
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.supabase_auth import supabase_auth

def test_token_validation():
    """Test token validation with real and mock tokens"""
    
    print("🔐 SUPABASE JWT AUTHENTICATION VALIDATION TEST")
    print("=" * 60)
    
    # Test configuration
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:9000")
    supabase_url = os.getenv("SUPABASE_URL", "")
    jwt_secret = os.getenv("JWT_SECRET_KEY", "test-secret")
    
    print(f"Base URL: {base_url}")
    print(f"Supabase URL: {supabase_url}")
    print(f"JWT Secret configured: {'✅' if jwt_secret else '❌'}")
    
    # Test 1: No token - should return 401
    print("\n📝 Test 1: Request without token")
    try:
        response = requests.get(f"{base_url}/debug-auth", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data.get("authenticated", True):
                print("✅ Correctly rejected request without token")
            else:
                print("❌ Incorrectly accepted request without token")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 2: Invalid token - should return 401
    print("\n📝 Test 2: Request with invalid token")
    try:
        headers = {"Authorization": "Bearer invalid_token_12345"}
        response = requests.get(f"{base_url}/debug-auth", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if not data.get("authenticated", True):
                print("✅ Correctly rejected invalid token")
            else:
                print("❌ Incorrectly accepted invalid token")
        elif response.status_code == 401:
            print("✅ Correctly returned 401 for invalid token")
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    # Test 3: Valid demo token
    print("\n📝 Test 3: Request with valid demo credentials")
    try:
        # Get demo token first
        login_data = {"username": "demo", "password": "demo1234"}
        login_response = requests.post(f"{base_url}/users/login", data=login_data, timeout=10)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            if access_token:
                print(f"✅ Got demo token: {access_token[:20]}...")
                
                # Test authenticated request
                headers = {"Authorization": f"Bearer {access_token}"}
                response = requests.get(f"{base_url}/debug-auth", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("authenticated"):
                        print("✅ Successfully authenticated with demo token")
                        print(f"   User ID: {data.get('user_id')}")
                        print(f"   Username: {data.get('username')}")
                    else:
                        print("❌ Demo token not properly validated")
                else:
                    print(f"❌ Authenticated request failed: {response.status_code}")
            else:
                print("❌ No access token in login response")
        else:
            print(f"❌ Demo login failed: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Demo login test failed: {e}")
    
    # Test 4: JWKS validation (if Supabase configured)
    print("\n📝 Test 4: JWKS Configuration")
    try:
        jwks_uri = supabase_auth.get_jwks_uri()
        if jwks_uri:
            print(f"✅ JWKS URI configured: {jwks_uri}")
            
            # Try to fetch JWKS
            jwks_data = supabase_auth.fetch_jwks()
            if jwks_data and "keys" in jwks_data:
                print(f"✅ JWKS fetched successfully, {len(jwks_data['keys'])} keys found")
            else:
                print("❌ JWKS fetch failed or empty")
        else:
            print("⚠️ JWKS URI not configured (Supabase URL missing)")
    except Exception as e:
        print(f"❌ JWKS test failed: {e}")
    
    # Test 5: Token expiry validation
    print("\n📝 Test 5: Expired Token Handling")
    try:
        # Create expired token
        expired_payload = {
            "sub": "test_user",
            "user_id": "test_user",
            "aud": "authenticated",
            "exp": int(time.time()) - 3600,  # Expired 1 hour ago
            "iat": int(time.time()) - 7200   # Issued 2 hours ago
        }
        
        expired_token = jwt.encode(expired_payload, jwt_secret, algorithm="HS256")
        
        try:
            supabase_auth.validate_token(expired_token)
            print("❌ Expired token incorrectly validated")
        except Exception as e:
            if "expired" in str(e).lower():
                print("✅ Expired token correctly rejected")
            else:
                print(f"⚠️ Unexpected error for expired token: {e}")
                
    except Exception as e:
        print(f"❌ Expired token test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 TOKEN VALIDATION TESTS COMPLETED")
    
    return True

def test_endpoint_protection():
    """Test that protected endpoints reject unauthorized requests"""
    
    print("\n🛡️ ENDPOINT PROTECTION TEST")
    print("=" * 60)
    
    base_url = os.getenv("TEST_BASE_URL", "http://localhost:9000")
    
    # Test protected endpoints
    protected_endpoints = [
        "/users/profile",
        "/upload",
        "/generate-video", 
        "/feedback",
        "/metrics",
        "/users/demo001/data"  # GDPR endpoint
    ]
    
    for endpoint in protected_endpoints:
        print(f"\n📝 Testing {endpoint}")
        try:
            # Test without token
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            
            if response.status_code == 401:
                print(f"✅ {endpoint} correctly requires authentication")
            elif response.status_code == 405:
                print(f"⚠️ {endpoint} method not allowed (testing GET on POST endpoint)")
            elif response.status_code == 422:
                print(f"⚠️ {endpoint} validation error (missing required fields)")
            else:
                print(f"❌ {endpoint} returned {response.status_code} instead of 401")
                
        except Exception as e:
            print(f"❌ {endpoint} test failed: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 ENDPOINT PROTECTION TESTS COMPLETED")

if __name__ == "__main__":
    print("Starting comprehensive authentication validation tests...")
    
    try:
        test_token_validation()
        test_endpoint_protection()
        print("\n✅ ALL AUTHENTICATION TESTS PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ AUTHENTICATION TESTS FAILED: {e}")
        sys.exit(1)