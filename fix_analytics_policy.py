#!/usr/bin/env python3

import os
import psycopg2

def fix_analytics_policy():
    """Fix analytics table RLS policy performance"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Fixing analytics table RLS policy...")
        
        # Check current policy
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'analytics' AND policyname = 'analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"Current policy: {result[0]}")
        
        # Drop and recreate with optimized pattern
        cursor.execute("DROP POLICY IF EXISTS analytics_policy ON public.analytics;")
        
        cursor.execute("""
            CREATE POLICY analytics_policy ON public.analytics
            USING (user_id::text = (select auth.uid())::text);
        """)
        
        conn.commit()
        
        # Verify fix
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'analytics' AND policyname = 'analytics_policy';
        """)
        
        result = cursor.fetchone()
        print(f"New policy: {result[0] if result else 'NOT FOUND'}")
        
        cursor.close()
        conn.close()
        
        print("SUCCESS: analytics_policy optimized")
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
    
    fix_analytics_policy()