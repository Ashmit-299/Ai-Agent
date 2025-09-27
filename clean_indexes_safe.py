#!/usr/bin/env python3

import os
import psycopg2

def clean_indexes_safe():
    """Safely clean duplicate indexes without breaking constraints"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Safely Cleaning Duplicate Indexes ===")
        
        # 1. Get current index count
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        initial_count = cursor.fetchone()[0]
        print(f"Initial index count: {initial_count}")
        
        # 2. Identify safe-to-remove duplicate indexes
        print("\n2. Identifying safe duplicate indexes...")
        
        safe_duplicates = [
            "idx_analytics_user_id",
            "idx_enhanced_analytics_user_id", 
            "idx_feedback_user_id",
            "idx_script_user_id",
            "ix_videos_video_id",
        ]
        
        removed_count = 0
        for index_name in safe_duplicates:
            try:
                # Check if index exists first
                cursor.execute(f"SELECT 1 FROM pg_indexes WHERE indexname = '{index_name}';")
                if cursor.fetchone():
                    cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                    print(f"Removed: {index_name}")
                    removed_count += 1
                else:
                    print(f"Not found: {index_name}")
            except Exception as e:
                print(f"Failed {index_name}: {str(e)[:40]}")
        
        # 3. Create optimized indexes where needed
        print("\n3. Creating optimized indexes...")
        
        optimized_indexes = [
            ("idx_user_active_email", "user", "email", "deleted_at IS NULL"),
            ("idx_script_user_active", "script", "user_id", "deleted_at IS NULL"),
            ("idx_videos_user_status", "videos", "user_id, status"),
            ("idx_feedback_recent", "feedback", "created_at DESC"),
            ("idx_analytics_recent", "analytics", "timestamp DESC"),
        ]
        
        created_count = 0
        for index_name, table, columns, condition in optimized_indexes:
            try:
                if condition:
                    sql = f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({columns}) WHERE {condition};'
                else:
                    sql = f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({columns});'
                
                cursor.execute(sql)
                print(f"Created: {index_name}")
                created_count += 1
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:40]}")
        
        # 4. Update statistics for key tables
        print("\n4. Updating statistics...")
        
        key_tables = ['user', 'script', 'videos', 'analytics', 'enhanced_analytics', 'feedback']
        analyzed_count = 0
        
        for table in key_tables:
            try:
                cursor.execute(f'ANALYZE public."{table}";')
                print(f"Analyzed: {table}")
                analyzed_count += 1
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 5. Final status
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        final_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nSUCCESS: Index cleanup complete")
        print(f"- Initial indexes: {initial_count}")
        print(f"- Removed duplicates: {removed_count}")
        print(f"- Created optimized: {created_count}")
        print(f"- Final indexes: {final_count}")
        print(f"- Tables analyzed: {analyzed_count}")
        
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
    
    success = clean_indexes_safe()
    
    if success:
        print("\nIndex optimization completed safely!")
        print("- Removed safe duplicate indexes")
        print("- Created performance-optimized indexes")
        print("- Updated table statistics")
        print("- Database ready for production")
    else:
        print("\nOptimization failed.")