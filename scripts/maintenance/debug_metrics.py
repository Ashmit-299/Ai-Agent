#!/usr/bin/env python3
"""Debug script to check what's in the database for metrics"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_database():
    """Check what's actually in the database"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"Database URL: {DATABASE_URL[:50]}...")
    
    if 'postgresql' in DATABASE_URL:
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Check each table
            tables = ['user', 'content', 'feedback', 'script']
            
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"{table}: {count} records")
                    
                    # Show sample data
                    if count > 0:
                        cur.execute(f"SELECT * FROM {table} LIMIT 3")
                        rows = cur.fetchall()
                        print(f"  Sample data: {len(rows)} rows")
                        for i, row in enumerate(rows):
                            print(f"    Row {i+1}: {row[:3]}...")  # First 3 columns only
                except Exception as e:
                    print(f"{table}: Error - {e}")
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"PostgreSQL connection failed: {e}")
    
    # Also check SQLite fallback
    try:
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        
        print("\nSQLite fallback database:")
        tables = ['user', 'content', 'feedback']
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                count = cur.fetchone()[0]
                print(f"{table}: {count} records")
            except Exception as e:
                print(f"{table}: Error - {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"SQLite check failed: {e}")

if __name__ == "__main__":
    debug_database()