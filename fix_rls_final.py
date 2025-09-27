#!/usr/bin/env python3

import os
import psycopg2

def fix_rls_final():
    """Final fix for RLS policies"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== FINAL RLS POLICY FIX ===")
        
        # Check current policies
        cursor.execute("""
            SELECT schemaname, tablename, policyname, qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        policies = cursor.fetchall()
        print(f"Found {len(policies)} policies to check")
        
        optimized_count = 0
        for schema, table, policy, qual in policies:
            print(f"\nChecking {table}.{policy}:")
            print(f"  Current: {qual[:80]}...")
            
            # Check if already optimized
            if "(select " in qual.lower():
                print(f"  Status: ALREADY OPTIMIZED")
                optimized_count += 1
            else:
                print(f"  Status: NEEDS OPTIMIZATION")
                
                try:
                    # Drop and recreate with optimization
                    cursor.execute(f"DROP POLICY IF EXISTS {policy} ON {schema}.{table};")
                    
                    # Apply optimization
                    new_qual = qual.replace("auth.uid()", "(select auth.uid())")
                    new_qual = new_qual.replace("auth.role()", "(select auth.role())")
                    
                    cursor.execute(f"CREATE POLICY {policy} ON {schema}.{table} USING ({new_qual});")
                    print(f"  Result: OPTIMIZED")
                    optimized_count += 1
                    
                except Exception as e:
                    print(f"  Result: FAILED - {str(e)[:50]}")
        
        conn.commit()
        
        # Verify optimization
        cursor.execute("""
            SELECT COUNT(*) FROM pg_policies 
            WHERE qual LIKE '%(select %'
            AND schemaname = 'public';
        """)
        
        final_optimized = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nFINAL RLS STATUS:")
        print(f"- Total policies: {len(policies)}")
        print(f"- Optimized in process: {optimized_count}")
        print(f"- Verified optimized: {final_optimized}")
        
        if final_optimized == len(policies):
            print(f"SUCCESS: All RLS policies optimized!")
        else:
            print(f"WARNING: {len(policies) - final_optimized} policies still need work")
        
        return final_optimized == len(policies)
        
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
    
    success = fix_rls_final()
    
    if success:
        print("\nALL RLS POLICIES SUCCESSFULLY OPTIMIZED!")
    else:
        print("\nRLS OPTIMIZATION INCOMPLETE")