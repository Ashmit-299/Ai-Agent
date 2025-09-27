#!/usr/bin/env python3

import os
import requests
import json

def fix_auth_rls_performance():
    """Fix Auth RLS performance using direct SQL execution"""
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return False
    
    try:
        # Prepare headers
        headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json'
        }
        
        print("Fixing Auth RLS Performance Issues...")
        
        # SQL to fix the policy
        sql_commands = [
            "DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;",
            """CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
               FOR ALL USING (user_id = (SELECT auth.uid()));"""
        ]
        
        for i, sql in enumerate(sql_commands, 1):
            print(f"{i}. Executing: {sql[:50]}...")
            
            # Execute SQL via REST API
            response = requests.post(
                f"{url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': sql}
            )
            
            if response.status_code not in [200, 201]:
                print(f"ERROR executing SQL: {response.status_code} - {response.text}")
                return False
        
        print("SUCCESS: Auth RLS performance optimized!")
        print("- Replaced auth.uid() with (SELECT auth.uid()) in enhanced_analytics_policy")
        
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
        print("\nAuth RLS performance issue resolved!")
        print("The enhanced_analytics policy now uses optimized auth function calls.")
    else:
        print("\nFailed to fix Auth RLS performance issue.")