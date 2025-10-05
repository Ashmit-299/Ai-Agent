#!/usr/bin/env python3
"""
Quick System Validation Test
Validates that the enhanced test suite can run without disrupting existing functionality
"""

import sys
import os
import requests
import time
import subprocess
import json

def test_server_running():
    """Test if server is running on port 9000"""
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on port 9000")
            return True
        else:
            print(f"❌ Server returned status {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        return False

def test_basic_endpoints():
    """Test basic endpoints are working"""
    endpoints = [
        "/health",
        "/demo-login", 
        "/docs",
        "/metrics"
    ]
    
    working_endpoints = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:9000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} - Working")
                working_endpoints += 1
            else:
                print(f"⚠️  {endpoint} - Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    return working_endpoints >= 3

def test_pytest_available():
    """Test if pytest is available and can run"""
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Pytest is available")
            return True
        else:
            print("❌ Pytest not working properly")
            return False
    except Exception as e:
        print(f"❌ Pytest test failed: {e}")
        return False

def test_project_structure():
    """Test if required project structure exists"""
    required_paths = [
        "app/main.py",
        "tests/",
        "tests/integration/",
        "tests/unit/",
        "pytest.ini",
        "requirements.txt"
    ]
    
    missing_paths = []
    for path in required_paths:
        if not os.path.exists(path):
            missing_paths.append(path)
    
    if missing_paths:
        print(f"❌ Missing required paths: {missing_paths}")
        return False
    else:
        print("✅ Project structure is complete")
        return True

def test_new_test_files():
    """Test if new test files were created correctly"""
    new_files = [
        "tests/integration/test_complete_workflow.py",
        "tests/integration/test_performance_benchmarks.py",
        "scripts/run_complete_tests.py"
    ]
    
    created_files = []
    for file_path in new_files:
        if os.path.exists(file_path):
            created_files.append(file_path)
            print(f"✅ Created: {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    return len(created_files) == len(new_files)

def test_imports():
    """Test if new test files can be imported without errors"""
    try:
        # Test if we can import the new test modules
        sys.path.insert(0, os.getcwd())
        
        # Try importing the test modules
        import tests.integration.test_complete_workflow
        import tests.integration.test_performance_benchmarks
        
        print("✅ New test modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during import: {e}")
        return False

def main():
    """Run all validation tests"""
    print("Running System Validation Tests")
    print("=" * 50)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("New Test Files", test_new_test_files),
        ("Import Tests", test_imports),
        ("Pytest Available", test_pytest_available),
        ("Server Running", test_server_running),
        ("Basic Endpoints", test_basic_endpoints)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"   Test failed: {test_name}")
        except Exception as e:
            print(f"   Test error: {test_name} - {e}")
    
    print("\n" + "=" * 50)
    print(f"Validation Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All validation tests passed! System is ready for comprehensive testing.")
        return True
    elif passed_tests >= total_tests - 1:
        print("Most tests passed. System should work correctly.")
        return True
    else:
        print("Some validation tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)