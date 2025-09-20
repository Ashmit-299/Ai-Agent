#!/usr/bin/env python3
"""
Test runner for AI Content Uploader Agent
"""

import subprocess
import sys
import time
import requests
import os

def wait_for_server(url="http://127.0.0.1:8000/health", timeout=30):
    """Wait for server to be ready"""
    print(f"⏳ Waiting for server at {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    
    print("❌ Server failed to start within timeout")
    return False

def run_backend_tests():
    """Run backend API tests"""
    print("\n🧪 Running all unit tests...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/", 
            "-v", "--tb=short"
        ], capture_output=True, text=True, timeout=300)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Unit tests timed out")
        return False
    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        return False

def run_smoke_test(num_users=5):
    """Run the concurrent smoke test"""
    print(f"\n🚀 Running smoke test with {num_users} users...")
    
    try:
        result = subprocess.run([
            sys.executable, "tests/smoke_test.py", 
            "--users", str(num_users)
        ], capture_output=True, text=True, timeout=120)
        
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("❌ Smoke test timed out")
        return False
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🧪 AI Content Uploader Agent - Test Suite")
    print("=" * 50)
    
    # Run backend API tests (don't need server running)
    backend_success = run_backend_tests()
    
    # Check if server is running for smoke tests
    server_running = wait_for_server()
    smoke_success = True
    
    if server_running:
        # Run smoke test
        smoke_success = run_smoke_test(num_users=5)
    else:
        print("\n⚠️ Server not running - skipping smoke tests")
        print("💡 To run smoke tests: python start_server_venv.py")
    
    if backend_success and smoke_success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())