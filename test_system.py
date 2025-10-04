#!/usr/bin/env python3
"""
System Integration Test
"""

import os
import subprocess
import time
import requests
from dotenv import load_dotenv

def test_database():
    print("Testing Database...")
    try:
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("SUCCESS: Database connected")
        return True
    except Exception as e:
        print(f"ERROR: Database failed - {e}")
        return False

def start_server():
    print("Starting Server...")
    try:
        # Start server
        process = subprocess.Popen(
            ["python", "scripts/start_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(8)
        
        # Test health
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("SUCCESS: Server running")
            return True, process
        else:
            print(f"ERROR: Server health failed - {response.status_code}")
            return False, process
    except Exception as e:
        print(f"ERROR: Server startup failed - {e}")
        return False, None

def test_endpoints():
    print("Testing Endpoints...")
    endpoints = [
        "/health",
        "/docs",
        "/demo-login", 
        "/contents",
        "/metrics"
    ]
    
    success = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:9000{endpoint}", timeout=3)
            if response.status_code in [200, 404]:
                print(f"  OK: {endpoint}")
                success += 1
            else:
                print(f"  FAIL: {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"  ERROR: {endpoint} - {e}")
    
    return success >= 3  # At least 3 endpoints working

def main():
    print("AI-Agent System Test")
    print("=" * 30)
    
    load_dotenv()
    
    # Test database
    db_ok = test_database()
    
    # Test server
    server_ok, process = start_server()
    
    # Test endpoints
    endpoints_ok = False
    if server_ok:
        endpoints_ok = test_endpoints()
    
    # Results
    print("\nResults:")
    print(f"Database: {'OK' if db_ok else 'FAIL'}")
    print(f"Server: {'OK' if server_ok else 'FAIL'}")
    print(f"Endpoints: {'OK' if endpoints_ok else 'FAIL'}")
    
    # Cleanup
    if process:
        process.terminate()
    
    if db_ok and server_ok and endpoints_ok:
        print("\nSUCCESS: All systems operational!")
    else:
        print("\nWARNING: Some systems need attention")

if __name__ == "__main__":
    main()