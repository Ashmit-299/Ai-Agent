#!/usr/bin/env python3
"""
Simple authentication solution for Swagger UI
"""

import requests
import json

def main():
    """Get fresh token and provide Swagger UI instructions"""
    base_url = "http://localhost:9000"
    
    print("=== Authentication Solution ===")
    print("Getting fresh authentication token...")
    
    # Get fresh token
    login_data = {"username": "demo", "password": "demo1234"}
    
    try:
        response = requests.post(f"{base_url}/users/login", data=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            print("SUCCESS: Fresh token obtained")
            print(f"Token: {access_token}")
            
            # Test the token
            headers = {"Authorization": f"Bearer {access_token}"}
            test_response = requests.get(f"{base_url}/debug-auth", headers=headers)
            
            if test_response.status_code == 200:
                debug_data = test_response.json()
                if debug_data.get("authenticated"):
                    print("SUCCESS: Token validation passed")
                    
                    print("\n" + "="*60)
                    print("SWAGGER UI AUTHORIZATION STEPS:")
                    print("="*60)
                    print("1. Open: http://localhost:9000/docs")
                    print("2. Click the green 'Authorize' button at the top")
                    print("3. In the 'Value' field, paste this token:")
                    print(f"   {access_token}")
                    print("4. Click 'Authorize' button")
                    print("5. Click 'Close' button")
                    print("6. All protected endpoints should now work!")
                    print("="*60)
                    
                    # Test a few key endpoints
                    print("\nTesting key endpoints:")
                    test_endpoints = ["/contents", "/metrics", "/users/profile"]
                    
                    for endpoint in test_endpoints:
                        try:
                            resp = requests.get(f"{base_url}{endpoint}", headers=headers)
                            status = "OK" if resp.status_code == 200 else f"ERROR {resp.status_code}"
                            print(f"  {endpoint}: {status}")
                        except Exception as e:
                            print(f"  {endpoint}: ERROR - {e}")
                    
                    return True
                else:
                    print("ERROR: Token validation failed")
            else:
                print(f"ERROR: Token test failed - {test_response.status_code}")
        else:
            print(f"ERROR: Login failed - {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"ERROR: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\nAuthentication is working correctly!")
        print("If you still see 401 errors:")
        print("- Make sure you authorized in Swagger UI")
        print("- Clear browser cache and refresh /docs")
        print("- Get a new token if this one expires")
    else:
        print("\nAuthentication setup failed!")
        print("Check if the server is running on port 9000")