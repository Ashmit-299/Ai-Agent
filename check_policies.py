#!/usr/bin/env python3
"""
Check current policy definitions
"""

import os
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get actual policy definitions
        cur.execute("""
            SELECT 
                tablename, 
                policyname, 
                qual,
                with_check
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
        """)
        
        results = cur.fetchall()
        
        print("Current Policy Definitions:")
        print("=" * 50)
        
        for table, policy, qual, with_check in results:
            print(f"\n{table}.{policy}:")
            if qual:
                print(f"  USING: {qual}")
            if with_check:
                print(f"  WITH CHECK: {with_check}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()