#!/usr/bin/env python3
"""
Final RLS verification - check for proper optimization patterns
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
        print("Final RLS Performance Verification")
        print("=" * 40)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check for optimized patterns
        cur.execute("""
            SELECT 
                tablename, 
                policyname, 
                CASE 
                    WHEN qual LIKE '%( SELECT auth.%' THEN 'OPTIMIZED'
                    WHEN qual LIKE '%auth.%' AND qual NOT LIKE '%( SELECT auth.%' THEN 'NEEDS_FIX'
                    ELSE 'NO_AUTH'
                END as optimization_status,
                qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
        """)
        
        results = cur.fetchall()
        
        print("RLS Policy Optimization Status:")
        print("-" * 50)
        
        optimized = 0
        needs_fix = 0
        no_auth = 0
        
        for table, policy, status, qual in results:
            print(f"{table}.{policy}: {status}")
            
            if status == 'OPTIMIZED':
                optimized += 1
            elif status == 'NEEDS_FIX':
                needs_fix += 1
            else:
                no_auth += 1
        
        print(f"\nSUMMARY:")
        print(f"Total Policies: {len(results)}")
        print(f"Optimized (using subqueries): {optimized}")
        print(f"Needs Fix (direct auth calls): {needs_fix}")
        print(f"No Auth Functions: {no_auth}")
        
        # Calculate optimization percentage
        auth_policies = optimized + needs_fix
        if auth_policies > 0:
            optimization_rate = (optimized / auth_policies) * 100
            print(f"Optimization Rate: {optimization_rate:.1f}%")
        
        if needs_fix == 0:
            print(f"\nSTATUS: ALL AUTH POLICIES OPTIMIZED")
            print("Auth RLS Initialization Plan warnings RESOLVED!")
            print("\nAll auth function calls are properly wrapped in subqueries:")
            print("- (SELECT auth.role()) instead of auth.role()")
            print("- (SELECT auth.uid()) instead of auth.uid()")
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