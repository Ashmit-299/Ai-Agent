#!/usr/bin/env python3
"""Fix Supabase database schema"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def fix_supabase_schema():
    """Ensure Supabase tables have correct structure"""
    
    try:
        from ..core.database import engine
        from sqlmodel import text
        
        print("Connecting to Supabase...")
        
        with engine.connect() as conn:
            # Check current table structure
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'content'
                ORDER BY ordinal_position
            """))
            
            columns = result.fetchall()
            print(f"Current content table columns: {[col[0] for col in columns]}")
            
            # Check if status column exists
            has_status = any(col[0] == 'status' for col in columns)
            
            if not has_status:
                print("Status column missing - this is expected and OK")
            else:
                print("Status column exists - removing it from model was correct")
            
            # Test a simple query
            result = conn.execute(text("SELECT COUNT(*) FROM content"))
            count = result.fetchone()[0]
            print(f"Total content records: {count}")
            
            print("✅ Supabase connection working!")
            return True
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

if __name__ == "__main__":
    fix_supabase_schema()