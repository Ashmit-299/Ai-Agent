#!/usr/bin/env python3
"""
Quick start script for the AI-Agent FastAPI server
"""

import os
import sys
import subprocess

def start_server():
    """Start the FastAPI server on port 9000"""
    print("Starting AI-Agent FastAPI Server...")
    print("Server will be available at: http://localhost:9000")
    print("API Documentation: http://localhost:9000/docs")
    print("Health Check: http://localhost:9000/health")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Start the server using uvicorn
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "9000"
        ]
        
        subprocess.run(cmd, cwd=os.getcwd())
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()