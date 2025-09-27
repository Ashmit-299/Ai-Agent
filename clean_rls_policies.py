#!/usr/bin/env python3

import os
import psycopg2

def clean_rls_policies():
    """Clean and properly optimize RLS policies"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== CLEANING RLS POLICIES ===")
        
        # Define clean, optimized policies for each table
        clean_policies = {
            'user': "((select auth.role()) = 'service_role' OR user_id::text = (select auth.uid())::text)",
            'script': "((select auth.role()) = 'service_role' OR user_id::text = (select auth.uid())::text)",
            'videos': "((select auth.role()) = 'service_role')",
            'analytics': "(user_id::text = (select auth.uid())::text)",
            'enhanced_analytics': "(user_id::text = (select auth.uid())::text)",
            'feedback': "((select auth.role()) = 'service_role' OR user_id::text = (select auth.uid())::text)",
            'system_logs': "((select auth.role()) = 'service_role')",
            'content': "((select auth.role()) = 'service_role' OR uploader::text = (select auth.uid())::text)",
            'invitations': "((select auth.role()) = 'service_role')",
            'test_connection': "((select auth.role()) = 'service_role')",
            'alembic_version': "((select auth.role()) = 'service_role')"
        }
        
        # Get current policies
        cursor.execute("""
            SELECT schemaname, tablename, policyname
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        
        current_policies = cursor.fetchall()
        
        # Clean and recreate each policy
        for schema, table, policy in current_policies:
            if table in clean_policies:
                try:
                    print(f"Cleaning {table}.{policy}...")
                    
                    # Drop existing policy
                    cursor.execute(f"DROP POLICY IF EXISTS {policy} ON {schema}.{table};")
                    
                    # Create clean optimized policy
                    clean_qual = clean_policies[table]
                    cursor.execute(f"CREATE POLICY {policy} ON {schema}.{table} USING ({clean_qual});")
                    
                    print(f"  SUCCESS: Clean policy created")
                    
                except Exception as e:
                    print(f"  FAILED: {str(e)[:50]}")
            else:
                print(f"Skipping {table} - no clean policy defined")
        
        conn.commit()
        
        # Verify results
        cursor.execute("""
            SELECT COUNT(*) FROM pg_policies 
            WHERE qual LIKE '%(select auth.%'
            AND schemaname = 'public';
        """)
        
        optimized_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nCLEAN RLS RESULTS:")
        print(f"- Policies processed: {len(current_policies)}")
        print(f"- Optimized policies: {optimized_count}")
        
        if optimized_count == len(current_policies):
            print(f"SUCCESS: All RLS policies are now clean and optimized!")
        else:
            print(f"WARNING: {len(current_policies) - optimized_count} policies may need manual review")
        
        return optimized_count == len(current_policies)
        
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
    
    success = clean_rls_policies()
    
    if success:
        print("\nALL RLS POLICIES CLEANED AND OPTIMIZED!")
        print("Supabase Performance Advisor warnings should now be resolved.")
    else:
        print("\nRLS CLEANING INCOMPLETE - Manual review may be needed")