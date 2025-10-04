#!/usr/bin/env python3
"""
Project Setup Script
Creates necessary directories and files that are excluded from git
"""

import os
import json
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    dirs = [
        'uploads',
        'logs', 
        'bucket/scripts',
        'bucket/storyboards',
        'bucket/videos',
        'bucket/logs',
        'bucket/ratings',
        'bucket/tmp',
        'bucket/uploads',
        'reports/failed_operations',
        'reports/failed_storyboards'
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def create_agent_state():
    """Create initial agent state file"""
    agent_state = {
        "q": {},
        "epsilon": 0.2
    }
    
    with open('agent_state.json', 'w') as f:
        json.dump(agent_state, f, indent=2)
    print("✓ Created agent_state.json")

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        env_content = """# AI Content Uploader Environment Variables

# Database Configuration
DATABASE_URL=sqlite:///./data.db

# JWT Secret
JWT_SECRET_KEY=dev-secret-key-change-in-production
JWS_SECRET=dev-jws-secret-change-in-production

# Storage Backend
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket

# Optional: External API Keys (leave empty for local development)
POSTHOG_API_KEY=
SENTRY_DSN=
PERPLEXITY_API_KEY=
BHIV_LM_URL=http://localhost:8001
BHIV_LM_API_KEY=demo_api_key_123
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
    else:
        print("✓ .env file already exists")

def create_database():
    """Initialize database"""
    try:
        from ..core.database import create_db_and_tables
        create_db_and_tables()
        print("✓ Database initialized")
    except Exception as e:
        print(f"⚠ Database initialization failed: {e}")

def main():
    """Run setup"""
    print("🚀 Setting up AI Content Uploader Agent...")
    print("=" * 50)
    
    create_directories()
    create_agent_state()
    create_env_file()
    create_database()
    
    print("=" * 50)
    print("✅ Setup complete!")
    print("\nNext steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Start server: python start_server.py")
    print("3. Run tests: python test_dashboard.py")

if __name__ == "__main__":
    main()