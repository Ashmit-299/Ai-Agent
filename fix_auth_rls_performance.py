#!/usr/bin/env python3

import os
import sys
from supabase import create_client, Client

def fix_auth_rls_performance():
    """Fix Auth RLS performance by optimizing auth function calls in policies"""
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        print("Fixing Auth RLS Performance Issues...")
        
        # Drop existing policy
        drop_policy_sql = """
        DROP POLICY IF EXISTS enhanced_analytics_policy ON public.enhanced_analytics;
        """
        
        # Create optimized policy with subquery for auth.uid()
        create_optimized_policy_sql = """
        CREATE POLICY enhanced_analytics_policy ON public.enhanced_analytics
        FOR ALL USING (
            user_id = (SELECT auth.uid())
        );
        """
        
        print("1. Dropping existing enhanced_analytics_policy...")
        result = supabase.rpc('exec_sql', {'sql': drop_policy_sql}).execute()
        
        print("2. Creating optimized enhanced_analytics_policy...")
        result = supabase.rpc('exec_sql', {'sql': create_optimized_policy_sql}).execute()
        
        print("SUCCESS: Auth RLS performance optimized!")
        print("- Replaced auth.uid() with (SELECT auth.uid()) in enhanced_analytics_policy")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def verify_fix():
    """Verify the RLS policy optimization"""
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        return False
    
    try:
        supabase: Client = create_client(url, key)
        
        # Check policy definition
        check_sql = """
        SELECT schemaname, tablename, policyname, definition
        FROM pg_policies 
        WHERE tablename = 'enhanced_analytics' 
        AND policyname = 'enhanced_analytics_policy';
        """
        
        result = supabase.rpc('exec_sql', {'sql': check_sql}).execute()
        
        if result.data and len(result.data) > 0:
            policy = result.data[0]
            definition = policy.get('definition', '')
            
            print(f"\nPolicy Definition: {definition}")
            
            # Check if it uses optimized pattern
            if "(select auth.uid())" in definition.lower():
                print("PASS: Policy uses optimized auth function call")
                return True
            else:
                print("FAIL: Policy still uses non-optimized auth function call")
                return False
        else:
            print("FAIL: Policy not found")
            return False
            
    except Exception as e:
        print(f"ERROR verifying fix: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Supabase Auth RLS Performance Fix ===")
    
    success = fix_auth_rls_performance()
    
    if success:
        print("\n=== Verification ===")
        verify_fix()
    
    sys.exit(0 if success else 1)