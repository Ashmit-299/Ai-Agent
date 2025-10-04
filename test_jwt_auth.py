#!/usr/bin/env python3
"""
Test JWT authentication configuration in OpenAPI schema
"""

import sys
import os

def test_jwt_auth_config():
    """Test if JWT authentication is properly configured in OpenAPI schema"""
    print("Testing JWT Authentication Configuration...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.getcwd())
        
        # Import the FastAPI app
        from app.main import app
        
        # Get OpenAPI schema
        schema = app.openapi()
        
        # Check if security schemes are defined
        components = schema.get('components', {})
        security_schemes = components.get('securitySchemes', {})
        
        print(f"Security schemes found: {list(security_schemes.keys())}")
        
        # Check for BearerAuth
        if 'BearerAuth' in security_schemes:
            bearer_auth = security_schemes['BearerAuth']
            print(f"BearerAuth configuration: {bearer_auth}")
            
            # Verify it's properly configured
            if bearer_auth.get('type') == 'http' and bearer_auth.get('scheme') == 'bearer':
                print("JWT Bearer authentication is properly configured!")
                
                # Check if any endpoints have security requirements
                paths = schema.get('paths', {})
                secured_endpoints = []
                
                for path, methods in paths.items():
                    for method, details in methods.items():
                        if 'security' in details:
                            secured_endpoints.append(f"{method.upper()} {path}")
                
                print(f"Secured endpoints found: {len(secured_endpoints)}")
                for endpoint in secured_endpoints[:5]:  # Show first 5
                    print(f"  - {endpoint}")
                
                if secured_endpoints:
                    print("Authentication is configured for specific endpoints!")
                else:
                    print("No endpoint-specific security found (using global or dependency-based auth)")
                
                return True
            else:
                print("BearerAuth not properly configured")
                return False
        else:
            print("BearerAuth security scheme not found")
            return False
            
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_auth_endpoints():
    """Test if authentication endpoints are available"""
    print("\nTesting Authentication Endpoints...")
    
    try:
        from app.main import app
        
        # Get all routes
        auth_routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                path = route.path
                if any(keyword in path.lower() for keyword in ['login', 'register', 'auth', 'token']):
                    methods = getattr(route, 'methods', ['GET'])
                    auth_routes.append(f"{list(methods)} {path}")
        
        print(f"Authentication-related routes found: {len(auth_routes)}")
        for route in auth_routes:
            print(f"  - {route}")
        
        if auth_routes:
            print("Authentication endpoints are available!")
            return True
        else:
            print("No authentication endpoints found")
            return False
            
    except Exception as e:
        print(f"Auth endpoints test failed: {e}")
        return False

if __name__ == "__main__":
    print("JWT Authentication Test")
    print("=" * 40)
    
    jwt_config_ok = test_jwt_auth_config()
    auth_endpoints_ok = test_auth_endpoints()
    
    print("\n" + "=" * 40)
    if jwt_config_ok and auth_endpoints_ok:
        print("JWT Authentication is properly configured!")
        print("\nTo test authentication:")
        print("1. Start the server: python quick_start.py")
        print("2. Go to: http://localhost:9000/docs")
        print("3. Look for the 'Authorize' button at the top")
        print("4. Get demo credentials from: http://localhost:9000/demo-login")
        print("5. Login at POST /users/login to get a token")
        print("6. Click 'Authorize' and enter your token")
    else:
        print("JWT Authentication configuration has issues")