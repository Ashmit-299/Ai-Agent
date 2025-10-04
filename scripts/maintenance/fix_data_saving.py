#!/usr/bin/env python3
"""Fix data saving to both local bucket and Supabase"""

import os
import sys
import time
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def create_missing_tables():
    """Create missing tables in both Supabase and SQLite"""
    
    try:
        # Try Supabase first
        from ..core.database import engine
        from sqlmodel import text
        
        print("Creating missing tables in Supabase...")
        
        with engine.connect() as conn:
            # Create script table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS script (
                    script_id TEXT PRIMARY KEY,
                    content_id TEXT,
                    user_id TEXT,
                    title TEXT,
                    script_content TEXT,
                    script_type TEXT DEFAULT 'text',
                    file_path TEXT,
                    created_at REAL,
                    used_for_generation BOOLEAN DEFAULT FALSE
                )
            """))
            
            # Create system_logs table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id SERIAL PRIMARY KEY,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    timestamp REAL,
                    user_id TEXT
                )
            """))
            
            # Create analytics table if not exists
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    event_type TEXT,
                    user_id TEXT,
                    content_id TEXT,
                    event_data TEXT,
                    timestamp REAL,
                    ip_address TEXT
                )
            """))
            
            conn.commit()
            print("[OK] Tables created in Supabase")
            
    except Exception as e:
        print(f"Supabase table creation failed: {e}")
    
    # Also create in SQLite fallback
    try:
        import sqlite3
        conn = sqlite3.connect('data.db')
        with conn:
            cur = conn.cursor()
            
            # Script table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS script (
                    script_id TEXT PRIMARY KEY,
                    content_id TEXT,
                    user_id TEXT,
                    title TEXT,
                    script_content TEXT,
                    script_type TEXT DEFAULT 'text',
                    file_path TEXT,
                    created_at REAL,
                    used_for_generation BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # System logs table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    timestamp REAL,
                    user_id TEXT
                )
            ''')
            
            # Analytics table
            cur.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT,
                    user_id TEXT,
                    content_id TEXT,
                    event_data TEXT,
                    timestamp REAL,
                    ip_address TEXT
                )
            ''')
            
        conn.close()
        print("[OK] Tables created in SQLite")
        
    except Exception as e:
        print(f"SQLite table creation failed: {e}")

def test_data_saving():
    """Test saving data to both bucket and database"""
    
    try:
        from core import bhiv_bucket
        
        # Test bucket saving
        test_data = {
            'test_id': 'test_123',
            'message': 'Test data saving',
            'timestamp': time.time()
        }
        
        # Save to different bucket segments
        bhiv_bucket.save_json('scripts', 'test_script.json', test_data)
        bhiv_bucket.save_json('logs', 'test_log.json', test_data)
        print("[OK] Bucket saving working")
        
        # Test database saving
        from ..core.database import DatabaseManager
        db = DatabaseManager()
        
        # Test script saving
        script_data = {
            'script_id': 'test_script_123',
            'content_id': 'test_content',
            'user_id': 'test_user',
            'title': 'Test Script',
            'script_content': 'This is a test script',
            'script_type': 'test',
            'file_path': 'test/path',
            'created_at': time.time(),
            'used_for_generation': False
        }
        
        try:
            db.create_script(script_data)
            print("[OK] Script saving to database working")
        except Exception as e:
            print(f"Script saving failed: {e}")
        
        print("[OK] Data saving test completed")
        
    except Exception as e:
        print(f"Data saving test failed: {e}")

if __name__ == "__main__":
    create_missing_tables()
    test_data_saving()