#!/usr/bin/env python3
"""
Simple server runner using current Python environment
"""
import uvicorn
import os

def main():
    """Start the server using current environment"""
    print("AI Content Uploader Agent - Starting Server")
    
    # Create directories
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    os.makedirs('bucket/tmp', exist_ok=True)
    
    print("Server: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")
    print("Press Ctrl+C to stop")
    
    # Start server with current Python environment
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()