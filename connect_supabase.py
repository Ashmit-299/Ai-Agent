#!/usr/bin/env python3
"""
Quick Supabase Connection Setup
Get your database password and connect to Supabase
"""

import os
from dotenv import load_dotenv, set_key

def connect_supabase():
    print("Supabase Connection Setup")
    print("=" * 30)
    
    # Load current .env
    load_dotenv()
    
    print("\nYou need your database password from Supabase:")
    print("1. Go to: https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc")
    print("2. Navigate: Settings > Database > Connection string")
    print("3. Copy the password from the connection string")
    
    # Get database password
    db_password = input("\nEnter your Supabase database password: ").strip()
    
    if db_password:
        # Update .env file
        set_key(".env", "SUPABASE_DB_PASSWORD", db_password)
        print("\nDatabase password saved to .env")
        
        # Test connection
        print("\nTesting connection...")
        try:
            from core.database import create_db_and_tables
            create_db_and_tables()
            print("SUCCESS: Supabase connected successfully!")
            
        except Exception as e:
            print(f"ERROR: Connection failed: {e}")
            print("\nTry using the full DATABASE_URL instead:")
            print("DATABASE_URL=postgresql://postgres.dusqpdhojbgfxwflukhc:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    
    else:
        print("ERROR: No password entered")

if __name__ == "__main__":
    connect_supabase()