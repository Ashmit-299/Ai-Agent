#!/usr/bin/env python3
"""
Fix Multiple Permissive Policies warnings - consolidate overlapping policies
"""

import os
import psycopg2
from dotenv import load_dotenv

def consolidate_policies(cur):
    """Consolidate multiple permissive policies into single policies"""
    
    print("Consolidating multiple permissive policies...")
    
    # Drop all existing policies
    cur.execute("""
        SELECT schemaname, tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public'
    """)
    
    policies = cur.fetchall()
    for schema, table, policy in policies:
        cur.execute(f'DROP POLICY IF EXISTS "{policy}" ON public."{table}";')
    
    print(f"Dropped {len(policies)} existing policies")
    
    # Create single comprehensive policies per table
    
    # User table - single policy
    cur.execute('''
        CREATE POLICY "user_policy" ON public."user"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            user_id = (SELECT auth.uid()::text)
        );
    ''')
    print("  User: 1 consolidated policy")
    
    # Content table - single policy
    cur.execute('''
        CREATE POLICY "content_policy" ON public."content"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            true
        );
    ''')
    print("  Content: 1 consolidated policy")
    
    # Script table - single policy (fixes the multiple SELECT policies issue)
    cur.execute('''
        CREATE POLICY "script_policy" ON public."script"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            true
        );
    ''')
    print("  Script: 1 consolidated policy")
    
    # Feedback table - single policy
    cur.execute('''
        CREATE POLICY "feedback_policy" ON public."feedback"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            true
        );
    ''')
    print("  Feedback: 1 consolidated policy")
    
    # Analytics tables - single policy each
    cur.execute('''
        CREATE POLICY "analytics_policy" ON public."analytics"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            user_id IS NULL OR 
            user_id = (SELECT auth.uid()::text)
        );
    ''')
    print("  Analytics: 1 consolidated policy")
    
    cur.execute('''
        CREATE POLICY "enhanced_analytics_policy" ON public."enhanced_analytics"
        FOR ALL USING (
            (SELECT auth.role()) = 'service_role' OR 
            user_id IS NULL OR 
            user_id = (SELECT auth.uid()::text)
        );
    ''')
    print("  Enhanced Analytics: 1 consolidated policy")
    
    # System tables - single policy each
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
                CREATE POLICY "{table}_policy" ON public."{table}"
                FOR ALL USING ((SELECT auth.role()) = 'service_role');
            ''')
            print(f"  {table}: 1 consolidated policy")

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Fix Multiple Permissive Policies")
        print("=" * 35)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Consolidate policies
        consolidate_policies(cur)
        
        conn.commit()
        
        # Verify - check for multiple policies per table/action
        cur.execute("""
            SELECT 
                tablename,
                cmd,
                COUNT(*) as policy_count
            FROM pg_policies 
            WHERE schemaname = 'public'
            GROUP BY tablename, cmd
            HAVING COUNT(*) > 1
            ORDER BY tablename, cmd;
        """)
        
        multiple_policies = cur.fetchall()
        
        print(f"\nVerification Results:")
        if multiple_policies:
            print("Tables with multiple policies for same action:")
            for table, cmd, count in multiple_policies:
                print(f"  {table}.{cmd}: {count} policies")
        else:
            print("No multiple permissive policies found!")
        
        # Show final policy count
        cur.execute("""
            SELECT tablename, COUNT(*) as total_policies
            FROM pg_policies 
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        total = sum(count for _, count in results)
        
        print(f"\nFinal Policy Count:")
        for table, count in results:
            print(f"  {table}: {count}")
        print(f"Total: {total}")
        
        status = "RESOLVED" if len(multiple_policies) == 0 else "NEEDS ATTENTION"
        print(f"\nMultiple Permissive Policies: {status}")
        
        cur.close()
        conn.close()
        
        return len(multiple_policies) == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()