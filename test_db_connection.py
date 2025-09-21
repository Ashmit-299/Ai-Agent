#!/usr/bin/env python3
"""Test Supabase database connection"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        from sqlmodel import create_engine, text
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Testing connection to: {DATABASE_URL[:50]}...")
        
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 10, "sslmode": "require"}
        )
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"SUCCESS: Connected to PostgreSQL: {version[:50]}...")
            
            # Test table creation
            conn.execute(text("CREATE TABLE IF NOT EXISTS test_connection (id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW())"))
            conn.execute(text("INSERT INTO test_connection DEFAULT VALUES"))
            result = conn.execute(text("SELECT COUNT(*) FROM test_connection"))
            count = result.fetchone()[0]
            print(f"SUCCESS: Database operations work. Test records: {count}")
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()