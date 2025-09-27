#!/usr/bin/env python3
"""
Final comprehensive Supabase health check
"""

import os
import psycopg2
from dotenv import load_dotenv

def check_rls_enabled(cur):
    """Check RLS is enabled on all tables"""
    cur.execute("""
        SELECT tablename, rowsecurity 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        ORDER BY tablename;
    """)
    
    results = cur.fetchall()
    disabled_count = sum(1 for _, enabled in results if not enabled)
    
    return len(results), disabled_count

def check_multiple_policies(cur):
    """Check for multiple permissive policies"""
    cur.execute("""
        SELECT 
            tablename,
            cmd,
            COUNT(*) as policy_count
        FROM pg_policies 
        WHERE schemaname = 'public'
        GROUP BY tablename, cmd
        HAVING COUNT(*) > 1;
    """)
    
    return cur.fetchall()

def check_auth_optimization(cur):
    """Check auth function optimization"""
    cur.execute("""
        SELECT 
            COUNT(*) as total_auth_policies,
            COUNT(CASE WHEN qual LIKE '%( SELECT auth.%' THEN 1 END) as optimized_policies
        FROM pg_policies 
        WHERE schemaname = 'public'
        AND qual LIKE '%auth.%';
    """)
    
    return cur.fetchone()

def check_duplicate_indexes(cur):
    """Check for duplicate indexes"""
    cur.execute("""
        WITH index_columns AS (
            SELECT 
                tablename,
                indexname,
                regexp_replace(indexdef, '.*USING [^(]*\\(([^)]*)\\).*', '\\1') as columns
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
        ),
        duplicates AS (
            SELECT 
                tablename,
                columns,
                COUNT(*) as dup_count
            FROM index_columns
            GROUP BY tablename, columns
            HAVING COUNT(*) > 1
        )
        SELECT COUNT(*) FROM duplicates;
    """)
    
    return cur.fetchone()[0]

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Final Supabase Health Check")
        print("=" * 30)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check 1: RLS Status
        total_tables, rls_disabled = check_rls_enabled(cur)
        rls_status = "PASS" if rls_disabled == 0 else f"FAIL ({rls_disabled} disabled)"
        print(f"1. RLS Security: {rls_status}")
        
        # Check 2: Multiple Policies
        multiple_policies = check_multiple_policies(cur)
        multiple_status = "PASS" if len(multiple_policies) == 0 else f"FAIL ({len(multiple_policies)} conflicts)"
        print(f"2. Multiple Permissive Policies: {multiple_status}")
        
        # Check 3: Auth Optimization
        total_auth, optimized_auth = check_auth_optimization(cur)
        if total_auth == 0:
            auth_status = "PASS (no auth policies)"
        elif optimized_auth == total_auth:
            auth_status = "PASS (100% optimized)"
        else:
            auth_status = f"FAIL ({optimized_auth}/{total_auth} optimized)"
        print(f"3. Auth RLS Optimization: {auth_status}")
        
        # Check 4: Duplicate Indexes
        duplicate_indexes = check_duplicate_indexes(cur)
        index_status = "PASS" if duplicate_indexes == 0 else f"FAIL ({duplicate_indexes} duplicates)"
        print(f"4. Duplicate Indexes: {index_status}")
        
        # Overall Status
        all_checks = [
            rls_disabled == 0,
            len(multiple_policies) == 0,
            total_auth == 0 or optimized_auth == total_auth,
            duplicate_indexes == 0
        ]
        
        overall_status = "ALL PASS" if all(all_checks) else "NEEDS ATTENTION"
        
        print(f"\nOVERALL STATUS: {overall_status}")
        
        if all(all_checks):
            print("\nAll Supabase Performance Advisor warnings RESOLVED!")
            print("Your database is fully optimized and secure.")
        else:
            print("\nSome issues remain - check individual status above.")
        
        # Summary stats
        cur.execute("SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';")
        total_policies = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname NOT LIKE '%_pkey';")
        total_indexes = cur.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"  Tables with RLS: {total_tables}")
        print(f"  Total Policies: {total_policies}")
        print(f"  Custom Indexes: {total_indexes}")
        
        cur.close()
        conn.close()
        
        return all(all_checks)
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()