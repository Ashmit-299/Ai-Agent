#!/usr/bin/env python3
"""
Database Connection Test
Quick test to verify your database configuration.
"""

import os
from dotenv import load_dotenv

def test_database_connection():
    print("🧪 AI-Agent Database Connection Test")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Check environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    database_url = os.getenv("DATABASE_URL")
    
    print(f"\n📋 Environment Check:")
    print(f"   SUPABASE_URL: {supabase_url}")
    print(f"   SUPABASE_ANON_KEY: {'✅ Set' if supabase_key else '❌ Not set'}")
    print(f"   DATABASE_URL: {database_url}")
    
    # Test database import
    try:
        print(f"\n🔄 Testing database import...")
        from core.database import DATABASE_URL, engine, create_db_and_tables
        
        print(f"✅ Database module imported successfully")
        print(f"🔗 Active connection: {DATABASE_URL}")
        
        # Test connection
        print(f"\n🔄 Testing database connection...")
        with engine.connect() as conn:
            if 'postgresql' in DATABASE_URL:
                result = conn.execute("SELECT version();")
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL connected: {version[:50]}...")
            else:
                result = conn.execute("SELECT sqlite_version();")
                version = result.fetchone()[0]
                print(f"✅ SQLite connected: {version}")
        
        # Test table creation
        print(f"\n🔄 Testing table creation...")
        create_db_and_tables()
        
        print(f"\n🎉 Database test completed successfully!")
        
        if 'sqlite' in DATABASE_URL:
            print(f"\n💡 Currently using SQLite. To switch to Supabase:")
            print(f"   1. Run: python setup_supabase.py")
            print(f"   2. Enter your Supabase credentials")
            print(f"   3. Restart your application")
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        print(f"\n🔧 Troubleshooting:")
        if 'postgresql' in str(e).lower() or 'supabase' in str(e).lower():
            print(f"   - Check your Supabase credentials")
            print(f"   - Verify network connectivity")
            print(f"   - Run: python setup_supabase.py")
        else:
            print(f"   - Check your .env file configuration")
            print(f"   - Ensure all dependencies are installed")

if __name__ == "__main__":
    test_database_connection()