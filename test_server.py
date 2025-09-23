#!/usr/bin/env python3
"""
Minimal server for testing registration
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-development")

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from app.auth import router as auth_router
    from app.models import UserRegister, Token
    
    # Create minimal app
    app = FastAPI(title="Test Registration Server")
    
    # Add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include auth router
    app.include_router(auth_router)
    
    @app.get("/")
    async def root():
        return {"message": "Test server running", "endpoints": ["/users/register", "/users/login"]}
    
    @app.get("/health")
    async def health():
        return {"status": "ok", "message": "Test server is healthy"}
    
    if __name__ == "__main__":
        import uvicorn
        print("Starting test server on http://localhost:8001")
        print("Test registration at: http://localhost:8001/users/register")
        print("API docs at: http://localhost:8001/docs")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies:")
    print("pip install fastapi uvicorn sqlmodel passlib[bcrypt] python-jose[cryptography]")
    sys.exit(1)
except Exception as e:
    print(f"Server startup error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)