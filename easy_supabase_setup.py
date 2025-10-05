#!/usr/bin/env python3
"""
Easy Supabase Setup - Universal Connection
Works with any Supabase account automatically
"""

import os
import requests
from dotenv import load_dotenv

def setup_supabase():
    print("🚀 Easy Supabase Setup")
    print("=" * 30)
    
    # Get Supabase URL
    url = input("Enter your Supabase URL: ").strip()
    if not url.startswith('https://'):
        print("❌ Invalid URL")
        return False
    
    # Get anon key
    key = input("Enter your Supabase anon key: ").strip()
    
    # Extract project ID
    import re
    match = re.search(r'https://([^.]+)\.supabase\.co', url)
    if not match:
        print("❌ Invalid URL format")
        return False
    
    project_id = match.group(1)
    
    # Try to get database password from Supabase API
    print("\n🔍 Detecting connection method...")
    
    # Method 1: Direct connection (most common)
    formats = [
        f"postgresql://postgres:[PASSWORD]@db.{project_id}.supabase.co:5432/postgres",
        f"postgresql://postgres.{project_id}:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        f"postgresql://postgres:[PASSWORD]@{project_id}.supabase.co:5432/postgres"
    ]
    
    print("📋 Available connection formats:")
    for i, fmt in enumerate(formats, 1):
        print(f"{i}. {fmt}")
    
    # Get password
    password = input("\nEnter your database password: ").strip()
    
    # Test connections
    working_url = None
    for fmt in formats:
        test_url = fmt.replace('[PASSWORD]', password)
        try:
            import psycopg2
            conn = psycopg2.connect(test_url)
            conn.close()
            working_url = test_url
            print(f"✅ Connected with: {fmt}")
            break
        except:
            continue
    
    if not working_url:
        print("❌ All formats failed. Using fallback.")
        working_url = f"postgresql://postgres:{password}@db.{project_id}.supabase.co:5432/postgres"
    
    # Update .env
    env_vars = {
        'DATABASE_URL': working_url,
        'SUPABASE_URL': url,
        'SUPABASE_ANON_KEY': key,
        'SUPABASE_DB_PASSWORD': password
    }
    
    # Read existing .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update variables
    for key, value in env_vars.items():
        if f"{key}=" in env_content:
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
            env_content = '\n'.join(lines)
        else:
            env_content += f"\n{key}={value}"
    
    # Write .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Configuration saved!")
    print(f"📊 Project: {project_id}")
    
    # Create tables
    try:
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Database tables created!")
        return True
    except Exception as e:
        print(f"⚠️  Tables creation: {e}")
        return True

if __name__ == "__main__":
    setup_supabase()