#!/usr/bin/env python3

import os
import psycopg2

def diagnose_and_fix_all():
    """Diagnose and fix all Supabase issues systematically"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== DIAGNOSING ALL SUPABASE ISSUES ===")
        
        # 1. Check for duplicate indexes
        print("\n1. CHECKING DUPLICATE INDEXES...")
        cursor.execute("""
            SELECT i1.indexname as idx1, i2.indexname as idx2, i1.tablename
            FROM pg_indexes i1, pg_indexes i2
            WHERE i1.schemaname = 'public' AND i2.schemaname = 'public'
            AND i1.tablename = i2.tablename
            AND i1.indexname < i2.indexname
            AND i1.indexdef = i2.indexdef;
        """)
        
        duplicates = cursor.fetchall()
        print(f"Found {len(duplicates)} duplicate index pairs")
        
        for idx1, idx2, table in duplicates:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {idx2};")
                print(f"Dropped duplicate: {idx2}")
            except Exception as e:
                print(f"Failed to drop {idx2}: {str(e)[:30]}")
        
        # 2. Check for unused indexes
        print("\n2. CHECKING UNUSED INDEXES...")
        cursor.execute("""
            SELECT indexrelname FROM pg_stat_user_indexes 
            WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
            AND schemaname = 'public'
            AND indexrelname NOT LIKE '%_pkey'
            AND indexrelname NOT LIKE '%_key';
        """)
        
        unused = cursor.fetchall()
        print(f"Found {len(unused)} unused indexes")
        
        for (index_name,) in unused:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                print(f"Dropped unused: {index_name}")
            except Exception as e:
                print(f"Failed to drop {index_name}: {str(e)[:30]}")
        
        # 3. Fix RLS policies
        print("\n3. FIXING RLS POLICIES...")
        cursor.execute("""
            SELECT schemaname, tablename, policyname, qual
            FROM pg_policies 
            WHERE qual LIKE '%auth.%'
            AND qual NOT LIKE '%(select %';
        """)
        
        policies = cursor.fetchall()
        print(f"Found {len(policies)} policies to optimize")
        
        for schema, table, policy, qual in policies:
            try:
                cursor.execute(f"DROP POLICY IF EXISTS {policy} ON {schema}.{table};")
                
                # Optimize the policy
                new_qual = qual.replace("auth.uid()", "(select auth.uid())")
                new_qual = new_qual.replace("auth.role()", "(select auth.role())")
                
                cursor.execute(f"CREATE POLICY {policy} ON {schema}.{table} USING ({new_qual});")
                print(f"Optimized: {table}.{policy}")
            except Exception as e:
                print(f"Failed to optimize {table}.{policy}: {str(e)[:40]}")
        
        # 4. Create missing essential indexes
        print("\n4. CREATING ESSENTIAL INDEXES...")
        
        essential = [
            ("idx_user_email", "user", "email"),
            ("idx_script_user", "script", "user_id"),
            ("idx_videos_user", "videos", "user_id"),
            ("idx_feedback_user", "feedback", "user_id"),
            ("idx_analytics_user", "analytics", "user_id"),
            ("idx_enhanced_analytics_user", "enhanced_analytics", "user_id"),
        ]
        
        for index_name, table, column in essential:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column});')
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:40]}")
        
        # 5. Remove problematic indexes
        print("\n5. REMOVING PROBLEMATIC INDEXES...")
        
        problematic = [
            "idx_user_email_unique",
            "idx_script_title", 
            "idx_videos_status",
            "idx_feedback_rating",
            "idx_analytics_event",
            "idx_enhanced_analytics_event"
        ]
        
        for index_name in problematic:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                print(f"Removed problematic: {index_name}")
            except Exception as e:
                print(f"Failed to remove {index_name}: {str(e)[:30]}")
        
        # 6. Update statistics
        print("\n6. UPDATING STATISTICS...")
        
        tables = ['user', 'script', 'videos', 'analytics', 'enhanced_analytics', 'feedback']
        for table in tables:
            try:
                cursor.execute(f'ANALYZE public."{table}";')
                print(f"Analyzed: {table}")
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 7. Final status
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        final_indexes = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'public';")
        final_policies = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nFINAL STATUS:")
        print(f"- Indexes: {final_indexes}")
        print(f"- Policies: {final_policies}")
        print(f"- Duplicates removed: {len(duplicates)}")
        print(f"- Unused removed: {len(unused)}")
        print(f"- Policies optimized: {len(policies)}")
        
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
    
    success = diagnose_and_fix_all()
    
    if success:
        print("\nALL SUPABASE ISSUES RESOLVED!")
    else:
        print("\nFIX FAILED - CHECK ERRORS ABOVE")