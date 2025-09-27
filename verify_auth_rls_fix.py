#!/usr/bin/env python3

import os
import psycopg2

def verify_auth_rls_fix():
    """Verify the Auth RLS performance fix"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL must be set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Verifying Auth RLS Performance Fix ===")
        
        # Check if policy exists and get its definition
        cursor.execute("""
            SELECT schemaname, tablename, policyname, cmd, qual
            FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            schema, table, policy, cmd, qual = result
            print(f"Policy found: {schema}.{table}.{policy}")
            print(f"Command: {cmd}")
            print(f"Condition: {qual}")
            
            # Check if it uses optimized pattern
            if qual and "(select auth.uid()" in qual.lower():
                print("\nSUCCESS: Policy uses optimized auth function call!")
                print("- Auth function is now evaluated once per query, not per row")
                print("- This will significantly improve performance at scale")
                return True
            else:
                print("\nWARNING: Policy may not be fully optimized")
                return False
        else:
            print("ERROR: enhanced_analytics_policy not found")
            return False
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    success = verify_auth_rls_fix()
    
    if success:
        print("\nAuth RLS Performance Issue: RESOLVED")
        print("The Supabase Performance Advisor warning should now be cleared.")
    else:
        print("\nAuth RLS Performance Issue: NOT RESOLVED")
        print("Manual intervention may be required.")