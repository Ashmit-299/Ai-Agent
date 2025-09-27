#!/usr/bin/env python3

import os
import psycopg2

def check_rls_status():
    """Check actual RLS policy status"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== CHECKING RLS POLICY STATUS ===")
        
        # Check all policies
        cursor.execute("""
            SELECT tablename, policyname, qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        policies = cursor.fetchall()
        
        optimized = 0
        for table, policy, qual in policies:
            print(f"\n{table}.{policy}:")
            print(f"  {qual}")
            
            if "(select auth." in qual.lower():
                print(f"  STATUS: OPTIMIZED")
                optimized += 1
            else:
                print(f"  STATUS: NOT OPTIMIZED")
        
        cursor.close()
        conn.close()
        
        print(f"\nSUMMARY:")
        print(f"- Total policies: {len(policies)}")
        print(f"- Optimized: {optimized}")
        print(f"- Not optimized: {len(policies) - optimized}")
        
        if optimized == len(policies):
            print(f"\nSUCCESS: All policies are optimized!")
        else:
            print(f"\nWARNING: {len(policies) - optimized} policies need work")
        
        return optimized == len(policies)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Load .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    check_rls_status()