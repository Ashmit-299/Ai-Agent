#!/usr/bin/env python3
"""
Fix Auth RLS Performance - Replace auth functions with subqueries
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_rls_policies(cur):
    """Replace auth functions with optimized subqueries"""
    
    print("Fixing RLS policy performance...")
    
    # Drop all existing policies first
    cur.execute("""
        SELECT schemaname, tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public'
    """)
    
    policies = cur.fetchall()
    for schema, table, policy in policies:
        cur.execute(f'DROP POLICY IF EXISTS "{policy}" ON public."{table}";')
    
    print(f"Dropped {len(policies)} existing policies")
    
    # Create optimized policies with subqueries
    
    # User table - optimized
    cur.execute('''
        CREATE POLICY "user_access_optimized" ON public."user"
        USING (
            (SELECT auth.role()) = 'service_role' OR 
            (SELECT auth.uid()::text) = user_id
        );
    ''')
    print("  Created optimized user policy")
    
    # Content table - optimized
    cur.execute('''
        CREATE POLICY "content_read_optimized" ON public."content"
        FOR SELECT USING (true);
    ''')
    
    cur.execute('''
        CREATE POLICY "content_write_optimized" ON public."content"
        FOR INSERT WITH CHECK (
            (SELECT auth.role()) = 'service_role' OR 
            (SELECT auth.uid()::text) = uploader_id
        );
    ''')
    
    cur.execute('''
        CREATE POLICY "content_update_optimized" ON public."content"
        FOR UPDATE USING (
            (SELECT auth.role()) = 'service_role' OR 
            (SELECT auth.uid()::text) = uploader_id
        );
    ''')
    print("  Created optimized content policies")
    
    # Script table - optimized
    cur.execute('''
        CREATE POLICY "script_read_optimized" ON public."script"
        FOR SELECT USING (true);
    ''')
    
    cur.execute('''
        CREATE POLICY "script_write_optimized" ON public."script"
        FOR INSERT WITH CHECK (
            (SELECT auth.role()) = 'service_role' OR 
            (SELECT auth.uid()::text) = user_id
        );
    ''')
    print("  Created optimized script policies")
    
    # Feedback table - optimized
    cur.execute('''
        CREATE POLICY "feedback_read_optimized" ON public."feedback"
        FOR SELECT USING (true);
    ''')
    
    cur.execute('''
        CREATE POLICY "feedback_write_optimized" ON public."feedback"
        FOR INSERT WITH CHECK (
            (SELECT auth.role()) = 'service_role' OR 
            (SELECT auth.uid()::text) = user_id
        );
    ''')
    print("  Created optimized feedback policies")
    
    # Analytics tables - optimized
    for table in ['analytics', 'enhanced_analytics']:
        cur.execute(f'''
            CREATE POLICY "{table}_access_optimized" ON public."{table}"
            USING (
                (SELECT auth.role()) = 'service_role' OR 
                user_id IS NULL OR 
                (SELECT auth.uid()::text) = user_id
            );
        ''')
        print(f"  Created optimized {table} policy")
    
    # System tables - service only
    system_tables = ['alembic_version', 'system_logs', 'test_connection', 'invitations', 'videos']
    for table in system_tables:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = %s
            );
        """, (table,))
        
        if cur.fetchone()[0]:
            cur.execute(f'''
                CREATE POLICY "{table}_service_optimized" ON public."{table}"
                USING ((SELECT auth.role()) = 'service_role');
            ''')
            print(f"  Created optimized {table} policy")

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Fix RLS Performance Issues")
        print("=" * 30)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Fix RLS policies
        fix_rls_policies(cur)
        
        conn.commit()
        
        # Verify final policies
        cur.execute("""
            SELECT tablename, policyname, qual
            FROM pg_policies 
            WHERE schemaname = 'public'
            ORDER BY tablename, policyname;
        """)
        
        results = cur.fetchall()
        
        print(f"\nFinal Policy Summary:")
        print(f"Total policies: {len(results)}")
        
        # Check for optimized patterns
        optimized_count = 0
        for table, policy, qual in results:
            if '(SELECT auth.' in qual:
                optimized_count += 1
        
        print(f"Optimized policies: {optimized_count}")
        print(f"Performance ratio: {optimized_count}/{len(results)}")
        
        if optimized_count == len(results):
            print("\nAll policies are performance-optimized!")
        else:
            print(f"\n{len(results) - optimized_count} policies still need optimization")
        
        print("Auth RLS Initialization Plan warnings should be RESOLVED!")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()