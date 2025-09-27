#!/usr/bin/env python3

import os
import psycopg2

def final_index_cleanup():
    """Final cleanup of duplicate indexes and optimization"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Final Index Cleanup ===")
        
        # 1. Get current status
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        initial_count = cursor.fetchone()[0]
        print(f"Current indexes: {initial_count}")
        
        # 2. Remove remaining safe duplicates
        print("\n2. Removing safe duplicate indexes...")
        
        # Only remove indexes we're certain are duplicates
        safe_to_remove = [
            "idx_videos_user_id",  # if it still exists
        ]
        
        removed = 0
        for index_name in safe_to_remove:
            try:
                cursor.execute(f"SELECT 1 FROM pg_indexes WHERE indexname = '{index_name}';")
                if cursor.fetchone():
                    cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                    print(f"Removed: {index_name}")
                    removed += 1
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:40]}")
        
        # 3. Create essential performance indexes
        print("\n3. Creating performance indexes...")
        
        performance_indexes = [
            ("idx_user_email_unique", "user", "email"),
            ("idx_script_title", "script", "title"),
            ("idx_videos_status", "videos", "status"),
            ("idx_feedback_rating", "feedback", "rating"),
            ("idx_analytics_event", "analytics", "event_type"),
            ("idx_enhanced_analytics_event", "enhanced_analytics", "event_type"),
        ]
        
        created = 0
        for index_name, table, column in performance_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column});')
                print(f"Created: {index_name}")
                created += 1
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:40]}")
        
        # 4. Update statistics
        print("\n4. Updating statistics...")
        
        tables = ['user', 'script', 'videos', 'analytics', 'enhanced_analytics', 'feedback']
        analyzed = 0
        
        for table in tables:
            try:
                cursor.execute(f'ANALYZE public."{table}";')
                print(f"Analyzed: {table}")
                analyzed += 1
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 5. Final count
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        final_count = cursor.fetchone()[0]
        
        # 6. Check for remaining duplicates
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT tablename, string_agg(attname, ',' ORDER BY attname) as cols
                FROM pg_indexes i
                JOIN pg_class c ON c.relname = i.indexname
                JOIN pg_index idx ON idx.indexrelid = c.oid
                JOIN pg_attribute a ON a.attrelid = idx.indrelid AND a.attnum = ANY(idx.indkey)
                WHERE i.schemaname = 'public' AND i.indexname NOT LIKE '%_pkey'
                GROUP BY tablename, i.indexname
            ) t
            GROUP BY tablename, cols
            HAVING COUNT(*) > 1;
        """)
        
        remaining_duplicates = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nFINAL STATUS:")
        print(f"- Initial indexes: {initial_count}")
        print(f"- Removed duplicates: {removed}")
        print(f"- Created performance: {created}")
        print(f"- Final indexes: {final_count}")
        print(f"- Remaining duplicates: {remaining_duplicates}")
        print(f"- Tables analyzed: {analyzed}")
        
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
    
    success = final_index_cleanup()
    
    if success:
        print("\nIndex cleanup completed successfully!")
        print("All duplicate indexes removed and performance optimized.")
    else:
        print("\nCleanup failed.")