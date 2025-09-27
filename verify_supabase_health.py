#!/usr/bin/env python3
"""
Verify Supabase database health and performance optimizations
"""

import os
import psycopg2
from dotenv import load_dotenv

def check_rls_status(cur):
    """Check RLS is enabled on all tables"""
    cur.execute("""
        SELECT tablename, rowsecurity 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        ORDER BY tablename;
    """)
    
    results = cur.fetchall()
    print("RLS Status:")
    all_enabled = True
    for table, rls_enabled in results:
        status = "ENABLED" if rls_enabled else "DISABLED"
        print(f"  {table}: {status}")
        if not rls_enabled:
            all_enabled = False
    
    return all_enabled

def check_policy_count(cur):
    """Check policy count per table"""
    cur.execute("""
        SELECT tablename, COUNT(*) as policy_count
        FROM pg_policies 
        WHERE schemaname = 'public'
        GROUP BY tablename
        ORDER BY tablename;
    """)
    
    results = cur.fetchall()
    print("\nPolicy Count (should be 1 per table):")
    optimal = True
    for table, count in results:
        status = "OPTIMAL" if count == 1 else f"WARNING ({count} policies)"
        print(f"  {table}: {status}")
        if count != 1:
            optimal = False
    
    return optimal

def check_indexes(cur):
    """Check performance indexes"""
    cur.execute("""
        SELECT COUNT(*) 
        FROM pg_indexes 
        WHERE schemaname = 'public' 
        AND indexname NOT LIKE '%_pkey';
    """)
    
    index_count = cur.fetchone()[0]
    print(f"\nPerformance Indexes: {index_count} created")
    return index_count > 0

def check_permissions(cur):
    """Check table permissions"""
    cur.execute("""
        SELECT grantee, table_name, privilege_type
        FROM information_schema.role_table_grants 
        WHERE table_schema = 'public'
        AND grantee IN ('authenticated', 'service_role')
        ORDER BY table_name, grantee;
    """)
    
    results = cur.fetchall()
    print(f"\nPermissions: {len(results)} grants configured")
    return len(results) > 0

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found or not PostgreSQL")
        return False
    
    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("\nSupabase Health Check")
        print("=" * 25)
        
        # Check all aspects
        rls_ok = check_rls_status(cur)
        policies_ok = check_policy_count(cur)
        indexes_ok = check_indexes(cur)
        permissions_ok = check_permissions(cur)
        
        # Overall health
        print("\nOverall Health:")
        print(f"  RLS Security: {'PASS' if rls_ok else 'FAIL'}")
        print(f"  Policy Optimization: {'PASS' if policies_ok else 'FAIL'}")
        print(f"  Performance Indexes: {'PASS' if indexes_ok else 'FAIL'}")
        print(f"  Permissions: {'PASS' if permissions_ok else 'FAIL'}")
        
        all_good = rls_ok and policies_ok and indexes_ok and permissions_ok
        
        print(f"\nFinal Status: {'ALL GOOD' if all_good else 'NEEDS ATTENTION'}")
        
        if all_good:
            print("\nSupabase Performance Advisor warnings should now be resolved!")
        
        cur.close()
        conn.close()
        
        return all_good
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()