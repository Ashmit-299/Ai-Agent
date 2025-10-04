#!/usr/bin/env python3
"""
Basic Test Runner - Simple validation of core functionality
"""

import sys
import os

def run_basic_tests():
    """Run basic system tests"""
    print("=== Basic System Tests ===")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Import core modules
    tests_total += 1
    try:
        from ..core.database import get_session, DatabaseManager
        from ..core.bhiv_bucket import save_text, init_bucket
        from ..app.main import app
        print("[PASS] Core module imports")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Core module imports: {e}")
    
    # Test 2: Database connection
    tests_total += 1
    try:
        db = DatabaseManager()
        analytics = db.get_analytics_data()
        print("[PASS] Database connection")
        tests_passed += 1
    except Exception as e:
        print(f"[FAIL] Database connection: {e}")
    
    # Test 3: Bucket initialization
    tests_total += 1
    try:
        if 'save_text' in locals():
            init_bucket()
            save_text("scripts", "test.txt", "test content")
            print("[PASS] Bucket operations")
            tests_passed += 1
        else:
            print("[SKIP] Bucket operations (import failed)")
    except Exception as e:
        print(f"[FAIL] Bucket operations: {e}")
    
    # Test 4: API health check
    tests_total += 1
    try:
        import requests
        response = requests.get('http://127.0.0.1:9000/health', timeout=2)
        if response.status_code == 200:
            print("[PASS] API health check")
            tests_passed += 1
        else:
            print(f"[FAIL] API health check: {response.status_code}")
    except Exception as e:
        print(f"[FAIL] API health check: {e}")
    
    # Summary
    print(f"\n=== Test Results ===")
    print(f"Passed: {tests_passed}/{tests_total}")
    
    if tests_passed == tests_total:
        print("[SUCCESS] All basic tests passed!")
        return 0
    else:
        print("[ERROR] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_basic_tests())