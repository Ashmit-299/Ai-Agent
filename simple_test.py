#!/usr/bin/env python3
"""
Simple Server Test Script
Quick verification that the AI Content Uploader Agent is working
"""

import requests
import time
import json

def test_server(base_url="http://127.0.0.1:9000"):
    """Test basic server functionality"""
    print("Testing AI Content Uploader Agent Server")
    print(f"Base URL: {base_url}")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("[PASS] Health check: PASSED")
            tests_passed += 1
        else:
            print(f"[FAIL] Health check: FAILED ({response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Health check: FAILED ({e})")
        tests_failed += 1
    
    # Test 2: Demo Login
    try:
        response = requests.get(f"{base_url}/demo-login", timeout=5)
        if response.status_code == 200:
            print("[PASS] Demo login: PASSED")
            tests_passed += 1
        else:
            print(f"[FAIL] Demo login: FAILED ({response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Demo login: FAILED ({e})")
        tests_failed += 1
    
    # Test 3: API Documentation
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("[PASS] API docs: PASSED")
            tests_passed += 1
        else:
            print(f"[FAIL] API docs: FAILED ({response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] API docs: FAILED ({e})")
        tests_failed += 1
    
    # Test 4: Contents List
    try:
        response = requests.get(f"{base_url}/contents", timeout=5)
        if response.status_code == 200:
            print("[PASS] Contents list: PASSED")
            tests_passed += 1
        else:
            print(f"[FAIL] Contents list: FAILED ({response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Contents list: FAILED ({e})")
        tests_failed += 1
    
    # Test 5: Metrics
    try:
        response = requests.get(f"{base_url}/metrics", timeout=5)
        if response.status_code == 200:
            print("[PASS] Metrics: PASSED")
            tests_passed += 1
        else:
            print(f"[FAIL] Metrics: FAILED ({response.status_code})")
            tests_failed += 1
    except Exception as e:
        print(f"[FAIL] Metrics: FAILED ({e})")
        tests_failed += 1
    
    print("=" * 50)
    print(f"Test Results: {tests_passed} passed, {tests_failed} failed")
    
    if tests_failed == 0:
        print("All tests passed! Server is working correctly.")
        return True
    else:
        print("Some tests failed. Check server configuration.")
        return False

if __name__ == "__main__":
    # Test default local server
    success = test_server()
    
    if not success:
        print("\nTroubleshooting tips:")
        print("1. Make sure the server is running: python start_server.py")
        print("2. Check if port 9000 is available")
        print("3. Verify dependencies are installed: pip install -r requirements.txt")