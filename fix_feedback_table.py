#!/usr/bin/env python3
"""
Fix feedback table - add missing ip_address column
"""
import os
from dotenv import load_dotenv

load_dotenv()

def fix_feedback_table():
    """Add missing ip_address column to feedback table"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Checking feedback table structure...")
        
        # Check if ip_address column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'feedback' AND column_name = 'ip_address'
        """)
        
        if not cur.fetchone():
            print("Adding missing ip_address column...")
            cur.execute("ALTER TABLE feedback ADD COLUMN IF NOT EXISTS ip_address VARCHAR")
            conn.commit()
            print("[OK] ip_address column added!")
        else:
            print("[OK] ip_address column already exists")
        
        # Verify final structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'feedback'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\nFinal feedback table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        cur.close()
        conn.close()
        
        print("\n[SUCCESS] Feedback table fixed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to fix feedback table: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Fixing Feedback Table")
    print("="*60)
    fix_feedback_table()
