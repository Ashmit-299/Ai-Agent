#!/usr/bin/env python3

import os
import psycopg2

def fix_user_policy_correct():
    """Fix user table RLS policy with correct column name"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Fixing user table RLS policy...")
        
        # Drop and recreate with optimized pattern
        cursor.execute("DROP POLICY IF EXISTS user_policy ON public.user;")
        
        # Create optimized policy - keep service_role access but optimize auth.uid()
        cursor.execute("""
            CREATE POLICY user_policy ON public.user
            USING (
                (select auth.role()) = 'service_role' OR 
                user_id::text = (select auth.uid())::text
            );
        """)
        
        conn.commit()
        
        # Verify fix
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'user' AND policyname = 'user_policy';
        """)
        
        result = cursor.fetchone()
        print(f"New policy: {result[0] if result else 'NOT FOUND'}")
        
        cursor.close()
        conn.close()
        
        print("SUCCESS: user_policy optimized with subquery pattern")
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
    
    fix_user_policy_correct()