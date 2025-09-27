#!/usr/bin/env python3

import os
import psycopg2
from urllib.parse import urlparse

def fix_auth_rls_performance():
    """Fix Auth RLS performance with proper type casting"""
    
    # Get database URL
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL must be set")
        return False
    
    try:
        print("Fixing Auth RLS Performance Issues...")
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # First, check the user_id column type
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'enhanced_analytics' 
            AND column_name = 'user_id';
        """)
        
        result = cursor.fetchone()
        user_id_type = result[0] if result else "unknown"
        print(f"user_id column type: {user_id_type}")
        
        # SQL commands to fix the policy with proper type casting
        sql_commands = [
            "DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;",
        ]
        
        # Create policy based on column type
        if user_id_type == "character varying":
            policy_sql = """CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
                           FOR ALL USING (user_id = (SELECT auth.uid()::text));"""
        else:
            policy_sql = """CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
                           FOR ALL USING (user_id::uuid = (SELECT auth.uid()));"""
        
        sql_commands.append(policy_sql)
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"{i}. Executing: {sql[:60]}...")
            cursor.execute(sql)
        
        # Commit changes
        conn.commit()
        
        print("SUCCESS: Auth RLS performance optimized!")
        print("- Replaced auth.uid() with (SELECT auth.uid()) with proper type casting")
        
        # Verify the fix
        cursor.execute("""
            SELECT definition 
            FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        result = cursor.fetchone()
        if result:
            definition = result[0]
            print(f"\nNew policy definition: {definition}")
            
            if "(select auth.uid()" in definition.lower():
                print("VERIFIED: Policy uses optimized auth function call")
            else:
                print("WARNING: Policy may not be fully optimized")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Supabase Auth RLS Performance Fix ===")
    
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    success = fix_auth_rls_performance()
    
    if success:
        print("\n✅ Auth RLS performance issue RESOLVED!")
        print("The enhanced_analytics policy now uses optimized auth function calls.")
        print("This will improve query performance at scale.")
    else:
        print("\n❌ Failed to fix Auth RLS performance issue.")