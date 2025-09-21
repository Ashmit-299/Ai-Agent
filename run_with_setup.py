#!/usr/bin/env python3
"""
Run project with automatic setup
"""

import os
import sys
import subprocess
import time

def setup_project():
    """Run setup if needed"""
    if not os.path.exists('bucket') or not os.path.exists('agent_state.json'):
        print("🔧 Running initial setup...")
        subprocess.run([sys.executable, 'setup_project.py'])
    else:
        print("✓ Project already set up")

def start_server():
    """Start the server"""
    print("🚀 Starting server...")
    try:
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '9000'
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

def main():
    """Main function"""
    setup_project()
    start_server()

if __name__ == "__main__":
    main()