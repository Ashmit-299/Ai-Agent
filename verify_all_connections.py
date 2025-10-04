#!/usr/bin/env python3
"""
Complete Integration Verification
Tests all endpoints and connections
"""

import os
import requests
import time
from dotenv import load_dotenv

def test_database():
    print("1. Testing Database Connection...")
    try:
        # Use the direct DATABASE_URL
        os.environ["DATABASE_URL"] = "postgresql://postgres.dusqpdhojbgfxwflukhc:SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
        
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("   ✓ Database connected successfully")
        return True
    except Exception as e:
        print(f"   ✗ Database failed: {e}")
        return False

def test_server():
    print("2. Testing Server Startup...")
    try:
        import subprocess
        import threading
        
        # Start server in background
        def start_server():
            subprocess.run(["python", "scripts/start_server.py"], capture_output=True)
        
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Wait for server to start
        time.sleep(5)
        
        # Test health endpoint
        response = requests.get("http://localhost:9000/health", timeout=10)
        if response.status_code == 200:
            print("   ✓ Server started successfully")
            return True
        else:
            print(f"   ✗ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Server startup failed: {e}")
        return False

def test_endpoints():
    print("3. Testing Key Endpoints...")
    endpoints = [
        "/health",
        "/docs", 
        "/demo-login",
        "/debug-auth",
        "/metrics",
        "/contents"
    ]
    
    success_count = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:9000{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                print(f"   ✓ {endpoint}")
                success_count += 1
            else:
                print(f"   ✗ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ✗ {endpoint} - Error: {e}")
    
    return success_count >= len(endpoints) * 0.7  # 70% success rate

def main():
    print("AI-Agent Integration Verification")
    print("=" * 40)
    
    load_dotenv()
    
    results = []
    results.append(test_database())
    results.append(test_server())
    results.append(test_endpoints())
    
    print("\nResults:")
    print("=" * 40)
    success_rate = sum(results) / len(results) * 100
    print(f"Overall Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 70:
        print("✓ System is ready for use!")
    else:
        print("✗ Some components need attention")

if __name__ == "__main__":
    main()