#!/usr/bin/env python3
"""
Start Server and Test Upload Fix
"""

import os
import sys
import time
import subprocess
import threading
from dotenv import load_dotenv

load_dotenv()

def start_server():
    """Start the FastAPI server"""
    print("[INFO] Starting FastAPI server...")
    
    try:
        # Start server in background
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(10)
        
        return process
        
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return None

def test_server():
    """Test if server is responding"""
    import requests
    
    for i in range(10):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("[SUCCESS] Server is responding")
                return True
        except:
            pass
        
        print(f"[INFO] Waiting for server... ({i+1}/10)")
        time.sleep(2)
    
    print("[ERROR] Server not responding after 20 seconds")
    return False

def main():
    """Main function"""
    print("AI-Agent Server Test")
    print("=" * 30)
    
    # Start server
    server_process = start_server()
    if not server_process:
        return False
    
    try:
        # Test server
        if not test_server():
            return False
        
        print("\n[INFO] Server started successfully!")
        print("You can now:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Test upload at http://localhost:8000/upload")
        print("3. Run: python test_upload_fix.py to test upload functionality")
        print("\nPress Ctrl+C to stop the server")
        
        # Keep server running
        server_process.wait()
        
    except KeyboardInterrupt:
        print("\n[INFO] Stopping server...")
        server_process.terminate()
        server_process.wait()
        return True
    
    except Exception as e:
        print(f"[ERROR] Server error: {e}")
        server_process.terminate()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)