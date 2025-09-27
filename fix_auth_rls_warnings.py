#!/usr/bin/env python3
"""
Fix auth RLS initialization plan warnings in Supabase
"""

import os
import psycopg2
from dotenv import load_dotenv

def drop_all_policies(cur):
    """Drop all existing policies"""
    cur.execute("""
        SELECT schemaname, tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public'
    """)
    
    policies = cur.fetchall()
    print(f"Dropping {len(policies)} existing policies...")
    
    for schema, table, policy in policies:
        cur.execute(f'DROP POLICY IF EXISTS "{policy}" ON public."{table}";')

def create_optimized_auth_policies(cur):
    """Create optimized RLS policies with proper auth functions"""
    
    # Get existing tables
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print("Creating optimized auth policies...")
    
    # User table - most restrictive
    if 'user' in tables:
        cur.execute('''
            CREATE POLICY "user_policy" ON public."user"
            FOR ALL USING (
                CASE 
                    WHEN auth.role() = 'service_role' THEN true
                    WHEN auth.uid() IS NOT NULL THEN auth.uid()::text = user_id
                    ELSE false
                END
            );
        ''')
        print("  Created optimized policy for user table")
    
    # Public read tables with owner write
    public_tables = ['content', 'script', 'feedback']
    for table in public_tables:
        if table in tables:
            if table == 'content':
                user_col = 'uploader_id'
            else:
                user_col = 'user_id'
                
            cur.execute(f'''
                CREATE POLICY "{table}_policy" ON public."{table}"
                FOR ALL USING (
                    CASE 
                        WHEN auth.role() = 'service_role' THEN true
                        WHEN TG_OP = 'SELECT' THEN true
                        WHEN auth.uid() IS NOT NULL THEN auth.uid()::text = {user_col}
                        ELSE false
                    END
                );
            ''')
            print(f"  Created optimized policy for {table} table")
    
    # Analytics tables - user data only
    analytics_tables = ['analytics', 'enhanced_analytics']
    for table in analytics_tables:
        if table in tables:
            cur.execute(f'''
                CREATE POLICY "{table}_policy" ON public."{table}"
                FOR ALL USING (
                    CASE 
                        WHEN auth.role() = 'service_role' THEN true
                        WHEN user_id IS NULL THEN true
                        WHEN auth.uid() IS NOT NULL THEN auth.uid()::text = user_id
                        ELSE false
                    END
                );
            ''')
            print(f"  Created optimized policy for {table} table")
    
    # System tables - service role only
    system_tables = ['alembic_version', 'system_logs', 'test_connection', 'invitations', 'videos']
    for table in system_tables:
        if table in tables:
            cur.execute(f'''
                CREATE POLICY "{table}_policy" ON public."{table}"
                FOR ALL USING (auth.role() = 'service_role');
            ''')
            print(f"  Created service-only policy for {table} table")

def optimize_auth_functions(cur):
    """Create optimized auth helper functions"""
    
    print("Creating auth helper functions...")
    
    # Function to check if user owns resource
    cur.execute('''
        CREATE OR REPLACE FUNCTION auth.user_owns_resource(resource_user_id text)
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT auth.uid()::text = resource_user_id;
        $$;
    ''')
    
    # Function to check service role
    cur.execute('''
        CREATE OR REPLACE FUNCTION auth.is_service_role()
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT auth.role() = 'service_role';
        $$;
    ''')
    
    # Function for public read access
    cur.execute('''
        CREATE OR REPLACE FUNCTION auth.can_read_public()
        RETURNS boolean
        LANGUAGE sql
        STABLE
        AS $$
            SELECT true;
        $$;
    ''')
    
    print("  Created auth helper functions")

def set_minimal_permissions(cur):
    """Set minimal required permissions"""
    
    print("Setting minimal permissions...")
    
    # Revoke all first
    cur.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM authenticated;")
    cur.execute("REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;")
    
    # Grant minimal permissions
    tables_to_grant = ['content', 'script', 'feedback', 'analytics', 'enhanced_analytics', 'user']
    
    for table in tables_to_grant:
        cur.execute(f'GRANT SELECT ON public."{table}" TO authenticated;')
        cur.execute(f'GRANT INSERT, UPDATE ON public."{table}" TO authenticated;')
    
    # Service role gets everything
    cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;")
    cur.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;")
    cur.execute("GRANT USAGE ON SCHEMA public TO authenticated;")
    
    print("  Minimal permissions set")

def add_auth_indexes(cur):
    """Add indexes to optimize auth queries"""
    
    print("Adding auth-optimized indexes...")
    
    auth_indexes = [
        ('user', 'idx_user_auth_uid', 'user_id'),
        ('content', 'idx_content_auth_uploader', 'uploader_id'),
        ('script', 'idx_script_auth_user', 'user_id'),
        ('feedback', 'idx_feedback_auth_user', 'user_id'),
        ('analytics', 'idx_analytics_auth_user', 'user_id'),
        ('enhanced_analytics', 'idx_enhanced_analytics_auth_user', 'user_id'),
    ]
    
    for table, index_name, column in auth_indexes:
        try:
            cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON public."{table}" ({column}) 
                WHERE {column} IS NOT NULL;
            ''')
            print(f"  Created auth index {index_name}")
        except Exception as e:
            print(f"  Skipped {index_name}: {e}")

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Step 1: Drop all existing policies
        drop_all_policies(cur)
        
        # Step 2: Create auth helper functions
        optimize_auth_functions(cur)
        
        # Step 3: Create optimized policies
        create_optimized_auth_policies(cur)
        
        # Step 4: Set minimal permissions
        set_minimal_permissions(cur)
        
        # Step 5: Add auth-optimized indexes
        add_auth_indexes(cur)
        
        conn.commit()
        
        # Verify
        cur.execute("""
            SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';
        """)
        policy_count = cur.fetchone()[0]
        
        print(f"\nOptimization complete!")
        print(f"Total policies: {policy_count}")
        print("Auth RLS initialization warnings should be resolved.")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Fix Auth RLS Initialization Warnings")
    print("=" * 40)
    main()