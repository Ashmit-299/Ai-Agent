#!/usr/bin/env python3

import os
import psycopg2

def fix_auth_rls_correct():
    """Fix Auth RLS with the exact pattern Supabase expects"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL must be set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Fixing Auth RLS Performance...")
        
        # Drop and recreate with exact Supabase-recommended pattern
        cursor.execute("DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;")
        
        # Use the exact pattern from Supabase docs
        cursor.execute("""
            CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
            FOR ALL USING (user_id::text = (select auth.uid()::text));
        """)
        
        conn.commit()
        
        # Verify the fix
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"New policy: {result[0]}")
            
        cursor.close()
        conn.close()
        
        print("SUCCESS: Auth RLS performance optimized with correct pattern")
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
    
    fix_auth_rls_correct()