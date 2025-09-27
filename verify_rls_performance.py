#!/usr/bin/env python3
"""
Verify RLS performance optimization
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
        print("RLS Performance Verification")
        print("=" * 30)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check all policies
        cur.execute("""
            SELECT 
                tablename, 
                policyname, 
                CASE 
                    WHEN qual LIKE '%(SELECT auth.%' THEN 'OPTIMIZED'
                    WHEN qual LIKE '%auth.%' THEN 'NEEDS_FIX'
                    ELSE 'NO_AUTH'
                END as performance_status
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
        """)
        
        results = cur.fetchall()
        
        print(f"Policy Performance Analysis:")
        print("-" * 40)
        
        optimized = 0
        needs_fix = 0
        no_auth = 0
        
        current_table = None
        for table, policy, status in results:
            if table != current_table:
                print(f"\n{table.upper()}:")
                current_table = table
            
            print(f"  {policy}: {status}")
            
            if status == 'OPTIMIZED':
                optimized += 1
            elif status == 'NEEDS_FIX':
                needs_fix += 1
            else:
                no_auth += 1
        
        print(f"\nSUMMARY:")
        print(f"Total Policies: {len(results)}")
        print(f"Optimized: {optimized}")
        print(f"Needs Fix: {needs_fix}")
        print(f"No Auth: {no_auth}")
        
        if needs_fix == 0:
            print(f"\nSTATUS: ALL OPTIMIZED ✓")
            print("Auth RLS Initialization Plan warnings RESOLVED!")
        else:
            print(f"\nSTATUS: {needs_fix} policies still need optimization")
        
        cur.close()
        conn.close()
        
        return needs_fix == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()