#!/usr/bin/env python3
"""
Quick server test script
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting test server...")
    print("Server: http://127.0.0.1:9000")
    print("API docs: http://127.0.0.1:9000/docs")
    print("Health check: http://127.0.0.1:9000/health")
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=9000, 
        reload=False,
        log_level="info"
    )