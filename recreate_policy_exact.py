#!/usr/bin/env python3

import os
import psycopg2

def recreate_policy_exact():
    """Recreate the policy with the exact Supabase recommended syntax"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("Recreating enhanced_analytics policy with exact Supabase syntax...")
        
        # Drop existing policy completely
        cursor.execute("DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;")
        
        # Create with the EXACT syntax from Supabase docs
        # The key is to use lowercase 'select' and no extra parentheses or aliases
        cursor.execute("""
            CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
            FOR ALL USING (user_id::text = (select auth.uid())::text);
        """)
        
        conn.commit()
        
        # Verify the exact syntax
        cursor.execute("""
            SELECT qual FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            qual = result[0]
            print(f"Policy created: {qual}")
            
            # Check for the exact pattern Supabase expects
            if "(select auth.uid())" in qual.lower():
                print("SUCCESS: Policy uses correct subquery pattern")
            else:
                print("WARNING: Policy may still not match Supabase expectations")
        
        cursor.close()
        conn.close()
        
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
    
    success = recreate_policy_exact()
    
    if success:
        print("\nPolicy recreated with exact Supabase syntax.")
        print("The Performance Advisor warning should be resolved.")
    else:
        print("\nFailed to recreate policy.")