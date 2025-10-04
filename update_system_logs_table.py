#!/usr/bin/env python3
"""
Update system_logs table to add missing columns for comprehensive logging
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def update_system_logs_table():
    """Add missing columns to system_logs table"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL or "postgresql" not in DATABASE_URL:
        print("No PostgreSQL DATABASE_URL configured")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Updating system_logs table...")
        
        # Add missing columns
        columns_to_add = [
            ("extra_data", "TEXT"),
            ("error_details", "TEXT"), 
            ("traceback", "TEXT")
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cur.execute(f"""
                    ALTER TABLE system_logs 
                    ADD COLUMN IF NOT EXISTS {column_name} {column_type}
                """)
                print(f"Added column: {column_name}")
            except Exception as e:
                print(f"Column {column_name} might already exist: {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'system_logs'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print("\nUpdated system_logs table structure:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        cur.close()
        conn.close()
        
        print("\n[SUCCESS] system_logs table updated successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to update table: {e}")
        return False

if __name__ == "__main__":
    print("=== Updating system_logs Table ===\n")
    success = update_system_logs_table()
    
    if success:
        print("\nTable update completed. You can now run test_system_logging.py again.")
    else:
        print("\nTable update failed. Check the error messages above.")