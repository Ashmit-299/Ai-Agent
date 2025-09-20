#!/usr/bin/env python3
"""
Simple server startup script
"""
import os
import sys
import subprocess

def main():
    """Start the server"""
    print("AI Content Uploader Agent - Quick Start")
    
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("Error: app/main.py not found. Run from project root.")
        sys.exit(1)
    
    # Use current Python executable
    python_exe = sys.executable
    
    # Create directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('bucket/tmp', exist_ok=True)
    
    # Start server
    cmd = [python_exe, '-m', 'uvicorn', 'app.main:app', '--reload', '--host', '0.0.0.0', '--port', '9000']
    
    print("Starting server...")
    print("Server: http://localhost:9000")
    print("API docs: http://localhost:9000/docs")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    main()