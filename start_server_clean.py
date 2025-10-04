#!/usr/bin/env python3
"""
Clean Server Start
"""
import os
import sys
import time
import subprocess

def kill_existing_servers():
    """Kill any existing servers on port 9000"""
    print("Checking for existing servers...")
    
    try:
        # Check what's using port 9000
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        pids_to_kill = []
        for line in lines:
            if ':9000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids_to_kill.append(pid)
        
        # Kill processes
        for pid in set(pids_to_kill):  # Remove duplicates
            try:
                subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
                print(f"Killed process {pid}")
            except:
                pass
        
        if pids_to_kill:
            print("Waiting for ports to be released...")
            time.sleep(2)
        
    except Exception as e:
        print(f"Error killing processes: {e}")

def start_server():
    """Start the server cleanly"""
    print("Starting AI Agent server...")
    
    try:
        # Import and test the app first
        from app.main import app
        print("App imported successfully")
        
        # Count routes
        routes = [route.path for route in app.routes if hasattr(route, 'path')]
        print(f"Found {len(routes)} routes")
        
        # Start server
        import uvicorn
        
        print("Starting server on http://127.0.0.1:9000")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=9000,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server start failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("AI AGENT SERVER STARTUP")
    print("=" * 40)
    
    # Kill existing servers
    kill_existing_servers()
    
    # Start fresh server
    start_server()