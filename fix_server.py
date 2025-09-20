#!/usr/bin/env python3
"""
Direct server runner that bypasses venv issues
"""
import subprocess
import sys
import os

def main():
    print("AI Content Uploader Agent - Direct Server Start")
    
    # Use venv python directly
    venv_python = os.path.join("venv", "Scripts", "python.exe")
    
    if not os.path.exists(venv_python):
        print("Error: Virtual environment not found")
        return
    
    # Install psycopg2-binary in venv if needed
    try:
        result = subprocess.run([venv_python, "-c", "import psycopg2"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("Installing psycopg2-binary in venv...")
            subprocess.run([venv_python, "-m", "pip", "install", "psycopg2-binary==2.9.9"])
    except Exception as e:
        print(f"Warning: {e}")
    
    # Create directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('bucket/tmp', exist_ok=True)
    
    print("Server: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    # Start server with venv python
    cmd = [venv_python, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nServer stopped")

if __name__ == "__main__":
    main()