#!/usr/bin/env python3
"""
Simple fix for auth RLS warnings - optimized policies only
"""

import os
import psycopg2
from dotenv import load_dotenv

def create_simple_optimized_policies(cur):
    """Create simple, optimized RLS policies"""
    
    # Get existing tables
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
    """)
    tables = [row[0] for row in cur.fetchall()]
    
    print("Creating simple optimized policies...")
    
    # User table
    if 'user' in tables:
        cur.execute('''
            CREATE POLICY "user_access" ON public."user"
            USING (auth.role() = 'service_role' OR auth.uid()::text = user_id);
        ''')
        print("  User table policy created")
    
    # Content table - public read, owner write
    if 'content' in tables:
        cur.execute('''
            CREATE POLICY "content_access" ON public."content"
            USING (auth.role() = 'service_role' OR true);
        ''')
        cur.execute('''
            CREATE POLICY "content_modify" ON public."content"
            FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.uid()::text = uploader_id);
        ''')
        cur.execute('''
            CREATE POLICY "content_update" ON public."content"
            FOR UPDATE USING (auth.role() = 'service_role' OR auth.uid()::text = uploader_id);
        ''')
        print("  Content table policies created")
    
    # Script table
    if 'script' in tables:
        cur.execute('''
            CREATE POLICY "script_access" ON public."script"
            USING (auth.role() = 'service_role' OR true);
        ''')
        cur.execute('''
            CREATE POLICY "script_modify" ON public."script"
            FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.uid()::text = user_id);
        ''')
        print("  Script table policies created")
    
    # Feedback table
    if 'feedback' in tables:
        cur.execute('''
            CREATE POLICY "feedback_access" ON public."feedback"
            USING (auth.role() = 'service_role' OR true);
        ''')
        cur.execute('''
            CREATE POLICY "feedback_modify" ON public."feedback"
            FOR INSERT WITH CHECK (auth.role() = 'service_role' OR auth.uid()::text = user_id);
        ''')
        print("  Feedback table policies created")
    
    # Analytics tables
    for table in ['analytics', 'enhanced_analytics']:
        if table in tables:
            cur.execute(f'''
                CREATE POLICY "{table}_access" ON public."{table}"
                USING (auth.role() = 'service_role' OR user_id IS NULL OR auth.uid()::text = user_id);
            ''')
            print(f"  {table} table policy created")
    
    # System tables - service only
    system_tables = ['alembic_version', 'system_logs', 'test_connection', 'invitations', 'videos']
    for table in system_tables:
        if table in tables:
            cur.execute(f'''
                CREATE POLICY "{table}_service_only" ON public."{table}"
                USING (auth.role() = 'service_role');
            ''')
            print(f"  {table} service-only policy created")

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
        
        # Drop existing policies
        cur.execute("""
            SELECT schemaname, tablename, policyname 
            FROM pg_policies 
            WHERE schemaname = 'public'
        """)
        
        policies = cur.fetchall()
        print(f"Dropping {len(policies)} existing policies...")
        
        for schema, table, policy in policies:
            cur.execute(f'DROP POLICY IF EXISTS "{policy}" ON public."{table}";')
        
        # Create optimized policies
        create_simple_optimized_policies(cur)
        
        conn.commit()
        
        # Verify
        cur.execute("""
            SELECT tablename, COUNT(*) as policy_count
            FROM pg_policies 
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        print(f"\nFinal policy count:")
        total = 0
        for table, count in results:
            print(f"  {table}: {count}")
            total += count
        
        print(f"Total policies: {total}")
        print("Auth RLS warnings should be resolved!")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Simple Auth RLS Fix")
    print("=" * 20)
    main()