#!/usr/bin/env python3
"""
Apply RLS fixes to Supabase database
"""

import os
import psycopg2
from dotenv import load_dotenv

def apply_rls_fixes():
    """Apply RLS security fixes to Supabase"""
    
    # Load environment variables
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("❌ DATABASE_URL not found or not PostgreSQL")
        return False
    
    try:
        # Read SQL file
        with open('fix_supabase_rls.sql', 'r') as f:
            sql_commands = f.read()
        
        # Connect to database
        print("Connecting to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Execute SQL commands
        print("Applying RLS security fixes...")
        cur.execute(sql_commands)
        conn.commit()
        
        print("RLS security fixes applied successfully!")
        
        # Verify RLS is enabled
        print("Verifying RLS status...")
        cur.execute("""
            SELECT schemaname, tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('enhanced_analytics', 'user', 'content', 'script', 'feedback', 'analytics', 'systemlogs')
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        print("\nRLS Status:")
        for schema, table, rls_enabled in results:
            status = "ENABLED" if rls_enabled else "DISABLED"
            print(f"  {table}: {status}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error applying RLS fixes: {e}")
        return False

if __name__ == "__main__":
    print("Supabase RLS Security Fix")
    print("=" * 40)
    
    success = apply_rls_fixes()
    
    if success:
        print("\nNext steps:")
        print("1. Check Supabase dashboard - Security warnings should be resolved")
        print("2. Test your API endpoints to ensure they still work")
        print("3. RLS policies are now protecting your data")
    else:
        print("\nFailed to apply fixes. Check your DATABASE_URL and try again.")