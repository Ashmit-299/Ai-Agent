#!/usr/bin/env python3

import os
import psycopg2

def final_verification():
    """Final verification of Auth RLS performance optimization"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL must be set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Final Auth RLS Performance Verification ===")
        
        # Check the policy condition
        cursor.execute("""
            SELECT schemaname, tablename, policyname, cmd, qual
            FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            schema, table, policy, cmd, qual = result
            print(f"Policy: {schema}.{table}.{policy}")
            print(f"Command: {cmd}")
            print(f"Condition: {qual}")
            
            # Check for optimized pattern (case insensitive)
            if qual and "select" in qual.lower() and "auth.uid()" in qual.lower():
                print("\nSUCCESS: Auth RLS Performance OPTIMIZED!")
                print("- Policy uses subquery: SELECT auth.uid()")
                print("- Auth function evaluated once per query, not per row")
                print("- Performance issue RESOLVED")
                
                # Show the optimization
                print(f"\nOptimized Pattern Found:")
                print(f"  Before: auth.uid() (evaluated per row)")
                print(f"  After:  SELECT auth.uid() (evaluated once per query)")
                
                return True
            else:
                print(f"\nCondition does not contain optimized pattern: {qual}")
                return False
        else:
            print("ERROR: Policy not found")
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
    
    success = final_verification()
    
    print("\n" + "="*50)
    if success:
        print("RESULT: Auth RLS Performance Issue RESOLVED")
        print("The Supabase Performance Advisor warning should be cleared.")
    else:
        print("RESULT: Auth RLS Performance Issue NEEDS ATTENTION")
    print("="*50)