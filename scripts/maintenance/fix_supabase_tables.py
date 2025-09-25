#!/usr/bin/env python3
"""
Fix Supabase tables - Create missing tables and columns
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def fix_supabase_tables():
    """Create missing tables in Supabase"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create feedback table with all required columns
        cur.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                content_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                watch_time_ms INTEGER DEFAULT 0,
                reward REAL DEFAULT 0.0,
                rating INTEGER,
                comment TEXT,
                sentiment TEXT,
                engagement_score REAL,
                timestamp REAL NOT NULL
            )
        """)
        
        # Create script table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS script (
                script_id TEXT PRIMARY KEY,
                content_id TEXT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                script_content TEXT NOT NULL,
                script_type TEXT DEFAULT 'text',
                file_path TEXT,
                created_at REAL NOT NULL,
                used_for_generation BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Create analytics table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT,
                content_id TEXT,
                event_data TEXT,
                timestamp REAL NOT NULL,
                ip_address TEXT
            )
        """)
        
        # Create system_logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                timestamp REAL NOT NULL,
                user_id TEXT
            )
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("Supabase tables created successfully!")
        return True
        
    except Exception as e:
        print(f"Failed to create Supabase tables: {e}")
        return False

if __name__ == "__main__":
    fix_supabase_tables()