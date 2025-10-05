#!/usr/bin/env python3
"""
Test 100% Success Validation
Validates that all issues are resolved for complete success
"""

import os
import sys
import subprocess
import time
import requests

def test_environment_setup():
    """Test that environment is properly configured"""
    print("Testing environment setup...")
    
    required_vars = [
        "DATABASE_URL", "JWT_SECRET_KEY", "ENVIRONMENT"
    ]
    
    all_set = True
    for var in required_vars:
        if os.getenv(var):
            print(f"PASS: {var} is set")
        else:
            print(f"FAIL: {var} is missing")
            all_set = False
    
    return all_set

def test_server_accessibility():
    """Test server is running and accessible"""
    print("Testing server accessibility...")
    
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("PASS: Server is accessible")
            return True
        else:
            print(f"FAIL: Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Server not accessible: {e}")
        return False

def test_authentication_flow():
    """Test authentication system works"""
    print("Testing authentication flow...")
    
    try:
        # Get demo credentials
        demo_response = requests.get("http://localhost:9000/demo-login", timeout=5)
        if demo_response.status_code != 200:
            print("FAIL: Demo login endpoint not accessible")
            return False
        
        demo_data = demo_response.json()
        username = demo_data.get('username', 'demo')
        password = demo_data.get('password', 'demo1234')
        
        # Test login
        login_response = requests.post(
            "http://localhost:9000/users/login",
            data={"username": username, "password": password},
            timeout=5
        )
        
        if login_response.status_code == 200:
            print("PASS: Authentication flow working")
            return True
        else:
            print(f"FAIL: Login failed with status {login_response.status_code}")
            return False
            
    except Exception as e:
        print(f"FAIL: Authentication test error: {e}")
        return False

def test_fixed_checklist():
    """Test the fixed pre-production checklist"""
    print("Testing fixed pre-production checklist...")
    
    try:
        result = subprocess.run([
            sys.executable, 
            "scripts/pre_production_checklist_fixed.py",
            "--api-url", "http://localhost:9000"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("PASS: Fixed checklist executed successfully")
            return True
        else:
            print(f"FAIL: Fixed checklist failed")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"FAIL: Error running fixed checklist: {e}")
        return False

def main():
    """Main test function"""
    print("Testing 100% Success Configuration")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("Server Accessibility", test_server_accessibility),
        ("Authentication Flow", test_authentication_flow),
        ("Fixed Checklist", test_fixed_checklist)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print("FINAL RESULTS")
    print("=" * 50)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    if passed == total:
        print("\n100% SUCCESS ACHIEVED!")
        print("All issues resolved")
        return True
    else:
        print(f"\n{total-passed} issues remaining")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)