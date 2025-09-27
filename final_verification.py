#!/usr/bin/env python3

import os
import psycopg2

def final_verification():
    """Final verification that all Supabase issues are resolved"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== FINAL VERIFICATION ===")
        
        # 1. Check for duplicate indexes
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT indexdef, COUNT(*) 
                FROM pg_indexes 
                WHERE schemaname = 'public' 
                GROUP BY indexdef 
                HAVING COUNT(*) > 1
            ) t;
        """)
        duplicates = cursor.fetchone()[0]
        
        # 2. Check optimized RLS policies
        cursor.execute("""
            SELECT COUNT(*) FROM pg_policies 
            WHERE qual LIKE '%(select %';
        """)
        optimized_policies = cursor.fetchone()[0]
        
        # 3. Check total policies
        cursor.execute("SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';")
        total_policies = cursor.fetchone()[0]
        
        # 4. Check essential indexes exist
        essential_indexes = ['idx_user_email', 'idx_script_user', 'idx_videos_user', 
                           'idx_feedback_user', 'idx_analytics_user', 'idx_enhanced_analytics_user']
        
        existing_essential = 0
        for index in essential_indexes:
            cursor.execute(f"SELECT 1 FROM pg_indexes WHERE indexname = '{index}';")
            if cursor.fetchone():
                existing_essential += 1
        
        # 5. Total indexes
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        total_indexes = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nVERIFICATION RESULTS:")
        print(f"- Duplicate indexes: {duplicates} (should be 0)")
        print(f"- Optimized RLS policies: {optimized_policies}/{total_policies}")
        print(f"- Essential indexes: {existing_essential}/{len(essential_indexes)}")
        print(f"- Total indexes: {total_indexes}")
        
        # Check if all issues are resolved
        all_resolved = (
            duplicates == 0 and
            optimized_policies == total_policies and
            existing_essential == len(essential_indexes)
        )
        
        if all_resolved:
            print(f"\nSUCCESS: ALL SUPABASE ISSUES RESOLVED!")
            print(f"- No duplicate indexes")
            print(f"- All RLS policies optimized")
            print(f"- All essential indexes created")
            print(f"- Database ready for production")
        else:
            print(f"\nWARNING: Some issues may remain")
            if duplicates > 0:
                print(f"- Still have {duplicates} duplicate indexes")
            if optimized_policies < total_policies:
                print(f"- {total_policies - optimized_policies} policies not optimized")
            if existing_essential < len(essential_indexes):
                print(f"- Missing {len(essential_indexes) - existing_essential} essential indexes")
        
        return all_resolved
        
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
    
    final_verification()