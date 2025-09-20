#!/usr/bin/env python3
"""
Dashboard Test - Test the Streamlit dashboard functionality
"""

import os
import sys
import requests
import time
import subprocess
import threading
from pathlib import Path

def test_dashboard_files():
    """Test if dashboard files exist"""
    print("Testing dashboard files...")
    
    required_files = [
        'streamlit_dashboard.py',
        'start_dashboard.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} exists")
        else:
            print(f"❌ {file} missing")
            return False
    
    return True

def test_dashboard_imports():
    """Test if required packages are available"""
    print("Testing dashboard imports...")
    
    required_packages = ['streamlit', 'plotly', 'pandas', 'requests']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} missing - installing...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
    
    return True

def test_api_connection():
    """Test API connection"""
    print("Testing API connection...")
    
    try:
        response = requests.get('http://127.0.0.1:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"⚠️ API server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("⚠️ API server not running - dashboard will work in demo mode")
        return False

def run_dashboard_test():
    """Run a quick dashboard test"""
    print("Starting dashboard test...")
    
    # Start dashboard in background
    dashboard_process = None
    try:
        dashboard_process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_dashboard.py',
            '--server.port', '8501',
            '--server.headless', 'true'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for startup
        time.sleep(5)
        
        # Test if dashboard is accessible
        try:
            response = requests.get('http://localhost:8501', timeout=10)
            if response.status_code == 200:
                print("✅ Dashboard is accessible")
                return True
            else:
                print(f"❌ Dashboard returned status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Dashboard not accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return False
    finally:
        if dashboard_process:
            dashboard_process.terminate()
            dashboard_process.wait()

def main():
    """Main test function"""
    print("🚀 BHIV Dashboard Test Suite")
    print("=" * 40)
    
    tests = [
        ("File Existence", test_dashboard_files),
        ("Package Imports", test_dashboard_imports),
        ("API Connection", test_api_connection),
        ("Dashboard Launch", run_dashboard_test)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Dashboard is ready to use.")
        print("Run 'python start_dashboard.py' to launch the dashboard.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)