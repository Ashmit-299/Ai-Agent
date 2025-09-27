#!/usr/bin/env python3
"""
Fix Supabase Performance Advisor warnings - clean up duplicate policies
"""

import os
import psycopg2
from dotenv import load_dotenv

def clean_duplicate_policies(cur):
    """Remove all existing policies to start fresh"""
    
    # Get all tables with RLS enabled
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print("Cleaning existing policies...")
    for table in tables:
        try:
            # Get existing policies for this table
            cur.execute("""
                SELECT policyname 
                FROM pg_policies 
                WHERE schemaname = 'public' 
                AND tablename = %s
            """, (table,))
            
            policies = [row[0] for row in cur.fetchall()]
            
            # Drop all existing policies
            for policy in policies:
                cur.execute(f'DROP POLICY IF EXISTS "{policy}" ON public."{table}";')
            
            if policies:
                print(f"  Removed {len(policies)} policies from {table}")
                
        except Exception as e:
            print(f"  Error cleaning {table}: {e}")

def create_optimized_policies(cur):
    """Create single, optimized policy per table"""
    
    policies = {
        'user': {
            'policy': 'user_access_policy',
            'sql': '''
                CREATE POLICY "user_access_policy" ON public."user"
                FOR ALL USING (
                    auth.uid()::text = user_id OR 
                    auth.role() = 'service_role'
                );
            '''
        },
        'content': {
            'policy': 'content_access_policy', 
            'sql': '''
                CREATE POLICY "content_access_policy" ON public."content"
                FOR ALL USING (
                    true OR 
                    auth.role() = 'service_role'
                );
            '''
        },
        'script': {
            'policy': 'script_access_policy',
            'sql': '''
                CREATE POLICY "script_access_policy" ON public."script"
                FOR ALL USING (
                    true OR 
                    auth.role() = 'service_role'
                );
            '''
        },
        'feedback': {
            'policy': 'feedback_access_policy',
            'sql': '''
                CREATE POLICY "feedback_access_policy" ON public."feedback"
                FOR ALL USING (
                    true OR 
                    auth.role() = 'service_role'
                );
            '''
        },
        'analytics': {
            'policy': 'analytics_access_policy',
            'sql': '''
                CREATE POLICY "analytics_access_policy" ON public."analytics"
                FOR ALL USING (
                    auth.uid()::text = user_id OR 
                    user_id IS NULL OR 
                    auth.role() = 'service_role'
                );
            '''
        },
        'enhanced_analytics': {
            'policy': 'enhanced_analytics_access_policy',
            'sql': '''
                CREATE POLICY "enhanced_analytics_access_policy" ON public."enhanced_analytics"
                FOR ALL USING (
                    auth.uid()::text = user_id OR 
                    user_id IS NULL OR 
                    auth.role() = 'service_role'
                );
            '''
        }
    }
    
    # Get existing tables
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
    """)
    existing_tables = [row[0] for row in cur.fetchall()]
    
    print("Creating optimized policies...")
    
    for table in existing_tables:
        try:
            if table in policies:
                # Create specific policy
                cur.execute(policies[table]['sql'])
                print(f"  Created policy for {table}")
            else:
                # Default service-role only policy for other tables
                cur.execute(f'''
                    CREATE POLICY "service_only_policy" ON public."{table}"
                    FOR ALL USING (auth.role() = 'service_role');
                ''')
                print(f"  Created default policy for {table}")
                
        except Exception as e:
            print(f"  Error creating policy for {table}: {e}")

def optimize_permissions(cur):
    """Set minimal required permissions"""
    
    print("Optimizing permissions...")
    
    # Revoke all existing permissions
    cur.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM authenticated;")
    cur.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;")
    
    # Grant minimal permissions to authenticated users
    tables_with_read_access = ['content', 'script', 'feedback']
    tables_with_write_access = ['analytics', 'enhanced_analytics', 'feedback']
    
    for table in tables_with_read_access:
        cur.execute(f'GRANT SELECT ON public."{table}" TO authenticated;')
    
    for table in tables_with_write_access:
        cur.execute(f'GRANT SELECT, INSERT, UPDATE ON public."{table}" TO authenticated;')
    
    # User table special permissions
    cur.execute('GRANT SELECT, UPDATE ON public."user" TO authenticated;')
    
    # Service role gets everything
    cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;")
    cur.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;")
    
    print("  Permissions optimized")

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
        
        # Step 1: Clean duplicate policies
        clean_duplicate_policies(cur)
        
        # Step 2: Create optimized policies
        create_optimized_policies(cur)
        
        # Step 3: Optimize permissions
        optimize_permissions(cur)
        
        conn.commit()
        
        # Verify final state
        print("\nVerifying final state...")
        cur.execute("""
            SELECT tablename, COUNT(*) as policy_count
            FROM pg_policies 
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        print("\nPolicy count per table:")
        total_policies = 0
        for table, count in results:
            print(f"  {table}: {count} policy")
            total_policies += count
        
        print(f"\nTotal policies: {total_policies}")
        
        cur.close()
        conn.close()
        
        print("Performance optimization completed!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Supabase Performance Optimization")
    print("=" * 35)
    main()