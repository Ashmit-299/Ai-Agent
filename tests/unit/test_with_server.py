#!/usr/bin/env python3
"""
Test with automatic server startup
"""

import subprocess
import time
import requests
import sys
import os

def start_server():
    """Start the API server in background"""
    try:
        # Start server process
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'app.main:app', 
            '--host', '127.0.0.1', '--port', '9000'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("Starting API server...")
        for i in range(10):
            try:
                response = requests.get('http://127.0.0.1:9000/health', timeout=2)
                if response.status_code == 200:
                    print("[SUCCESS] API server started on port 9000")
                    return process
            except:
                time.sleep(1)
        
        print("[ERROR] Server failed to start")
        process.terminate()
        return None
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return None

def run_tests():
    """Run the dashboard tests"""
    try:
        result = subprocess.run([sys.executable, 'test_dashboard.py'], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Test execution failed: {e}")
        return False

def main():
    print("=== Automated Test with Server ===")
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("[ERROR] Cannot start server, running tests anyway...")
        return run_tests()
    
    try:
        # Run tests
        success = run_tests()
        return success
    finally:
        # Clean up server
        if server_process:
            server_process.terminate()
            print("\n[INFO] Server stopped")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)