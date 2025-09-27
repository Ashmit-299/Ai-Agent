#!/usr/bin/env python3

import os
import psycopg2

def final_policy_fix():
    """Final attempt with minimal syntax"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Final policy fix with minimal syntax...")
        
        # Drop and recreate with absolute minimal syntax
        cursor.execute("DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;")
        
        # Minimal syntax - exactly as Supabase docs show
        cursor.execute("""
            CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
            USING (user_id = (select auth.uid())::text);
        """)
        
        conn.commit()
        
        # Check result
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        print(f"Final policy: {result[0] if result else 'NOT FOUND'}")
        
        cursor.close()
        conn.close()
        
        print("SUCCESS: Policy recreated with minimal syntax")
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
    
    final_policy_fix()