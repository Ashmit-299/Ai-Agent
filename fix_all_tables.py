#!/usr/bin/env python3
"""
Fix all database tables - ensure all columns exist
"""
import os
from dotenv import load_dotenv

load_dotenv()

def fix_all_tables():
    """Fix all database tables"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Fixing all database tables...")
        print("="*60)
        
        # Fix content table
        print("\n1. Checking content table...")
        content_columns = [
            ("duration_ms", "INTEGER DEFAULT 0"),
            ("views", "INTEGER DEFAULT 0"),
            ("likes", "INTEGER DEFAULT 0"),
            ("shares", "INTEGER DEFAULT 0")
        ]
        
        for col_name, col_type in content_columns:
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'content' AND column_name = '{col_name}'
            """)
            
            if not cur.fetchone():
                print(f"  Adding {col_name}...")
                cur.execute(f"ALTER TABLE content ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                conn.commit()
                print(f"  [OK] {col_name} added!")
            else:
                print(f"  [OK] {col_name} exists")
        
        # Fix feedback table
        print("\n2. Checking feedback table...")
        feedback_columns = [
            ("sentiment", "VARCHAR"),
            ("engagement_score", "FLOAT"),
            ("ip_address", "VARCHAR")
        ]
        
        for col_name, col_type in feedback_columns:
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'feedback' AND column_name = '{col_name}'
            """)
            
            if not cur.fetchone():
                print(f"  Adding {col_name}...")
                cur.execute(f"ALTER TABLE feedback ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                conn.commit()
                print(f"  [OK] {col_name} added!")
            else:
                print(f"  [OK] {col_name} exists")
        
        # Fix script table
        print("\n3. Checking script table...")
        script_columns = [
            ("version", "VARCHAR DEFAULT '1.0'"),
            ("script_metadata", "TEXT")
        ]
        
        for col_name, col_type in script_columns:
            cur.execute(f"""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'script' AND column_name = '{col_name}'
            """)
            
            if not cur.fetchone():
                print(f"  Adding {col_name}...")
                cur.execute(f"ALTER TABLE script ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                conn.commit()
                print(f"  [OK] {col_name} added!")
            else:
                print(f"  [OK] {col_name} exists")
        
        cur.close()
        conn.close()
        
        print("\n" + "="*60)
        print("[SUCCESS] All tables fixed!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to fix tables: {e}")
        return False

if __name__ == "__main__":
    fix_all_tables()
    print("\nNext steps:")
    print("1. Restart the server: python scripts/start_server.py")
    print("2. Test feedback endpoint: POST /feedback")
    print("3. Test content endpoint: GET /contents")
