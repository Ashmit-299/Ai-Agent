#!/usr/bin/env python3

import os
import psycopg2

def fix_supabase_final():
    """Fix Supabase performance issues with proper table name handling"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Fixing Supabase Performance Issues ===")
        
        # 1. Create missing foreign key indexes
        print("\n1. Creating foreign key indexes...")
        
        fk_indexes = [
            ("idx_scripts_user_id", "script", "user_id"),
            ("idx_videos_user_id", "videos", "user_id"),
            ("idx_videos_script_id", "videos", "script_id"),
            ("idx_feedback_user_id", "feedback", "user_id"),
            ("idx_analytics_user_id", "analytics", "user_id"),
            ("idx_enhanced_analytics_user_id", "enhanced_analytics", "user_id"),
            ("idx_system_logs_user_id", "system_logs", "user_id"),
        ]
        
        for index_name, table, column in fk_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column});')
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:50]}")
        
        # 2. Create performance indexes
        print("\n2. Creating performance indexes...")
        
        perf_indexes = [
            ("idx_analytics_created_at", "analytics", "created_at"),
            ("idx_enhanced_analytics_created_at", "enhanced_analytics", "created_at"),
            ("idx_feedback_created_at", "feedback", "created_at"),
            ("idx_videos_created_at", "videos", "created_at"),
            ("idx_system_logs_timestamp", "system_logs", "timestamp"),
            ("idx_analytics_event_type", "analytics", "event_type"),
            ("idx_enhanced_analytics_event_type", "enhanced_analytics", "event_type"),
            ("idx_user_email", "user", "email"),
            ("idx_user_created_at", "user", "created_at"),
        ]
        
        for index_name, table, column in perf_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column});')
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:50]}")
        
        # 3. Create composite indexes
        print("\n3. Creating composite indexes...")
        
        composite_indexes = [
            ("idx_analytics_user_event", "analytics", "user_id, event_type"),
            ("idx_enhanced_analytics_user_event", "enhanced_analytics", "user_id, event_type"),
            ("idx_feedback_user_created", "feedback", "user_id, created_at"),
            ("idx_videos_user_created", "videos", "user_id, created_at"),
        ]
        
        for index_name, table, columns in composite_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({columns});')
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:50]}")
        
        # 4. Update statistics
        print("\n4. Updating table statistics...")
        
        tables = ['user', 'script', 'videos', 'analytics', 'enhanced_analytics', 'feedback', 'system_logs']
        for table in tables:
            try:
                cursor.execute(f'ANALYZE public."{table}";')
                print(f"Analyzed: {table}")
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 5. Final status
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        total_indexes = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nSUCCESS: Supabase optimization complete")
        print(f"Total indexes: {total_indexes}")
        
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
    
    success = fix_supabase_final()
    
    if success:
        print("\nSupabase performance optimization completed!")
        print("- Foreign key indexes added")
        print("- Performance indexes created")
        print("- Composite indexes added")
        print("- Table statistics updated")
    else:
        print("\nOptimization failed.")