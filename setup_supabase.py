#!/usr/bin/env python3
"""
Supabase Setup and Connection Test Script
This script helps you configure and test your Supabase connection.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test Supabase database connection with different formats"""
    
    print("🔍 Testing Supabase Connection...")
    print("=" * 50)
    
    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY") 
    supabase_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Anon Key: {supabase_key[:20]}..." if supabase_key else "Anon Key: Not found")
    print(f"JWT Secret: {supabase_jwt_secret[:20]}..." if supabase_jwt_secret else "JWT Secret: Not found")
    
    if not all([supabase_url, supabase_key, supabase_jwt_secret]):
        print("❌ Missing Supabase credentials!")
        return False
    
    # Extract project ID from URL
    import re
    match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
    if not match:
        print("❌ Invalid Supabase URL format!")
        return False
    
    project_id = match.group(1)
    print(f"Project ID: {project_id}")
    
    # Test different connection formats
    connection_formats = [
        # Format 1: Direct connection (most common)
        f"postgresql://postgres:{supabase_jwt_secret}@db.{project_id}.supabase.co:5432/postgres",
        
        # Format 2: Pooler connection
        f"postgresql://postgres.{project_id}:{supabase_jwt_secret}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        
        # Format 3: Alternative pooler
        f"postgresql://postgres:{supabase_jwt_secret}@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true&connection_limit=1",
    ]
    
    print("\n🧪 Testing connection formats...")
    
    for i, conn_str in enumerate(connection_formats, 1):
        print(f"\nFormat {i}: Testing connection...")
        print(f"Connection: {conn_str[:60]}...")
        
        try:
            import psycopg2
            conn = psycopg2.connect(conn_str)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()
            cur.close()
            conn.close()
            
            print(f"✅ SUCCESS! Connection format {i} works!")
            print(f"Database version: {version[0][:50]}...")
            
            # Update .env file with working connection
            update_env_file(conn_str)
            return True
            
        except Exception as e:
            print(f"❌ Format {i} failed: {str(e)[:100]}...")
            continue
    
    print("\n❌ All connection formats failed!")
    print("\n📋 Please check:")
    print("1. Your Supabase project is active")
    print("2. Database password is correct")
    print("3. Your IP is allowed (check Supabase dashboard)")
    print("4. Try resetting your database password in Supabase dashboard")
    
    return False

def update_env_file(working_connection):
    """Update .env file with working connection string"""
    try:
        # Read current .env file
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        # Update DATABASE_URL line
        updated_lines = []
        for line in lines:
            if line.startswith('DATABASE_URL='):
                updated_lines.append(f'DATABASE_URL={working_connection}\n')
                print(f"✅ Updated DATABASE_URL in .env file")
            else:
                updated_lines.append(line)
        
        # Write back to .env file
        with open('.env', 'w') as f:
            f.writelines(updated_lines)
            
    except Exception as e:
        print(f"⚠️ Could not update .env file: {e}")

def create_supabase_tables():
    """Create required tables in Supabase"""
    print("\n🏗️ Creating Supabase tables...")
    
    try:
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def main():
    print("🚀 Supabase Setup Script")
    print("=" * 50)
    
    # Test connection
    if test_supabase_connection():
        print("\n✅ Supabase connection successful!")
        
        # Create tables
        if create_supabase_tables():
            print("\n🎉 Supabase setup complete!")
            print("\nNext steps:")
            print("1. Run: python scripts/start_server.py")
            print("2. Test: curl http://localhost:9000/health")
        else:
            print("\n⚠️ Connection works but table creation failed")
    else:
        print("\n❌ Supabase setup failed")
        print("\nFalling back to SQLite for development...")
        
        # Update to use SQLite
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace(
                'DATABASE_URL=postgresql://', 
                '# DATABASE_URL=postgresql://'
            )
            content += '\n# Fallback to SQLite\nDATABASE_URL=sqlite:///./ai_agent.db\n'
            
            with open('.env', 'w') as f:
                f.write(content)
                
            print("✅ Updated .env to use SQLite fallback")
            
        except Exception as e:
            print(f"⚠️ Could not update .env: {e}")

if __name__ == "__main__":
    main()