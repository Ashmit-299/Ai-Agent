#!/usr/bin/env python3

import os
import psycopg2

def check_all_auth_policies():
    """Check all policies for auth function usage"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Checking ALL policies for auth function usage ===")
        
        # Find all policies with auth functions
        cursor.execute("""
            SELECT schemaname, tablename, policyname, qual
            FROM pg_policies 
            WHERE qual ILIKE '%auth.%'
            ORDER BY tablename, policyname;
        """)
        
        policies = cursor.fetchall()
        
        print(f"Found {len(policies)} policies with auth functions:")
        
        for schema, table, policy, qual in policies:
            print(f"\nTable: {table}")
            print(f"Policy: {policy}")
            print(f"Condition: {qual}")
            
            # Check if it needs optimization
            if "auth.uid()" in qual and "SELECT" not in qual.upper():
                print("  ❌ NEEDS OPTIMIZATION: Direct auth.uid() call")
            elif "SELECT" in qual.upper() and "auth.uid()" in qual:
                print("  ✅ OPTIMIZED: Uses subquery pattern")
            else:
                print("  ⚠️  UNKNOWN: Check manually")
        
        cursor.close()
        conn.close()
        
        return True
        
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
    
    check_all_auth_policies()