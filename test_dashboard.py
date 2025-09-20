#!/usr/bin/env python3
"""
Dashboard Test Script
Tests dashboard functionality and API connections
"""

import requests
import time
import sys

def test_api_connection():
    """Test API server connection"""
    try:
        response = requests.get('http://127.0.0.1:9000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
            return True
        else:
            print(f"❌ API server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running on port 9000")
        return False
    except Exception as e:
        print(f"❌ API connection error: {e}")
        return False

def test_dashboard_endpoints():
    """Test dashboard data endpoints"""
    endpoints = [
        '/bhiv/analytics',
        '/metrics',
        '/tasks/queue/stats'
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:9000{endpoint}', timeout=5)
            results[endpoint] = response.status_code == 200
            status = "✅" if results[endpoint] else "❌"
            print(f"{status} {endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = False
            print(f"❌ {endpoint}: {e}")
    
    return all(results.values())

def test_dashboard_imports():
    """Test dashboard module imports"""
    try:
        import streamlit
        print("✅ Streamlit import successful")
    except ImportError:
        print("❌ Streamlit not installed")
        return False
    
    try:
        import plotly
        print("✅ Plotly import successful")
    except ImportError:
        print("❌ Plotly not installed")
        return False
    
    try:
        import pandas
        print("✅ Pandas import successful")
    except ImportError:
        print("❌ Pandas not installed")
        return False
    
    return True

def main():
    """Run all dashboard tests"""
    print("🧪 Dashboard Test Suite")
    print("=" * 40)
    
    # Test imports
    print("\n📦 Testing imports...")
    imports_ok = test_dashboard_imports()
    
    # Test API connection
    print("\n🔗 Testing API connection...")
    api_ok = test_api_connection()
    
    # Test endpoints if API is running
    endpoints_ok = True
    if api_ok:
        print("\n📊 Testing dashboard endpoints...")
        endpoints_ok = test_dashboard_endpoints()
    else:
        print("\n⚠️ Skipping endpoint tests (API not running)")
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    print(f"  Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  API Connection: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"  Endpoints: {'✅ PASS' if endpoints_ok else '❌ FAIL'}")
    
    if imports_ok and api_ok and endpoints_ok:
        print("\n🎉 All tests passed! Dashboard is ready.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())