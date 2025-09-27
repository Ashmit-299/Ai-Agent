#!/usr/bin/env python3

import os
import psycopg2

def fix_all_auth_policies():
    """Fix all policies with non-optimized auth function calls"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Fixing ALL Auth RLS Performance Issues ===")
        
        # Find policies that need optimization
        cursor.execute("""
            SELECT schemaname, tablename, policyname, qual
            FROM pg_policies 
            WHERE qual ILIKE '%auth.uid()%'
            AND qual NOT ILIKE '%SELECT%auth.uid()%'
            ORDER BY tablename;
        """)
        
        policies_to_fix = cursor.fetchall()
        
        if not policies_to_fix:
            print("No policies found that need auth optimization")
            return True
        
        print(f"Found {len(policies_to_fix)} policies to optimize:")
        
        for schema, table, policy, qual in policies_to_fix:
            print(f"Fixing {table}.{policy}...")
            
            # Drop existing policy
            cursor.execute(f"DROP POLICY IF EXISTS {policy} ON {schema}.{table};")
            
            # Create optimized policy based on table
            if table == "enhanced_analytics":
                cursor.execute(f"""
                    CREATE POLICY {policy} ON {schema}.{table}
                    FOR ALL USING (user_id::text = (select auth.uid()::text));
                """)
            else:
                # Generic optimization for other tables
                optimized_qual = qual.replace("auth.uid()", "(select auth.uid())")
                cursor.execute(f"""
                    CREATE POLICY {policy} ON {schema}.{table}
                    FOR ALL USING ({optimized_qual});
                """)
            
            print(f"  Optimized {table}.{policy}")
        
        conn.commit()
        
        print(f"\nSUCCESS: Optimized {len(policies_to_fix)} policies")
        
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
    
    success = fix_all_auth_policies()
    
    if success:
        print("\nAll Auth RLS performance issues should now be resolved.")
    else:
        print("\nFailed to fix Auth RLS performance issues.")