#!/usr/bin/env python3
"""
Create Audit Logs Table in Supabase
"""

import os
import psycopg2
from dotenv import load_dotenv

def create_audit_table():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("❌ PostgreSQL DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create audit_logs table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                timestamp REAL NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                request_id TEXT,
                details TEXT,
                status TEXT DEFAULT 'success',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for performance
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
        """)
        
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
        """)
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("✅ Audit logs table created in Supabase")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create audit table: {e}")
        return False

if __name__ == "__main__":
    create_audit_table()