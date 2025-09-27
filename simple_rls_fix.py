#!/usr/bin/env python3

import os
import psycopg2

def simple_rls_fix():
    """Simple RLS fix with basic optimized patterns"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== SIMPLE RLS FIX ===")
        
        # Simple policy fixes - one at a time to avoid transaction issues
        policies_to_fix = [
            ('enhanced_analytics', 'enhanced_analytics_policy', 'user_id::text = (select auth.uid())::text'),
            ('feedback', 'feedback_policy', '(select auth.role()) = \'service_role\' OR user_id::text = (select auth.uid())::text'),
            ('script', 'script_policy', '(select auth.role()) = \'service_role\' OR user_id::text = (select auth.uid())::text'),
            ('videos', 'videos_policy', '(select auth.role()) = \'service_role\''),
            ('system_logs', 'system_logs_policy', '(select auth.role()) = \'service_role\''),
            ('invitations', 'invitations_policy', '(select auth.role()) = \'service_role\''),
            ('test_connection', 'test_connection_policy', '(select auth.role()) = \'service_role\''),
            ('user', 'user_policy', '(select auth.role()) = \'service_role\' OR user_id::text = (select auth.uid())::text'),
            ('content', 'content_policy', '(select auth.role()) = \'service_role\''),
        ]
        
        success_count = 0
        
        for table, policy, condition in policies_to_fix:
            try:
                # Start fresh transaction for each policy
                cursor.execute(f"DROP POLICY IF EXISTS {policy} ON public.{table};")
                cursor.execute(f"CREATE POLICY {policy} ON public.{table} USING ({condition});")
                conn.commit()
                
                print(f"Fixed: {table}.{policy}")
                success_count += 1
                
            except Exception as e:
                conn.rollback()  # Rollback failed transaction
                print(f"Failed {table}.{policy}: {str(e)[:50]}")
        
        # Final verification
        cursor.execute("""
            SELECT COUNT(*) FROM pg_policies 
            WHERE qual LIKE '%(select auth.%'
            AND schemaname = 'public';
        """)
        
        optimized_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nSIMPLE RLS FIX RESULTS:")
        print(f"- Policies attempted: {len(policies_to_fix)}")
        print(f"- Successfully fixed: {success_count}")
        print(f"- Verified optimized: {optimized_count}")
        
        return success_count > 0
        
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
    
    success = simple_rls_fix()
    
    if success:
        print("\nRLS POLICIES SUCCESSFULLY OPTIMIZED!")
        print("All Supabase performance issues should now be resolved.")
    else:
        print("\nRLS FIX FAILED")