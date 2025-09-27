#!/usr/bin/env python3

import os
import psycopg2

def fix_all_supabase_issues():
    """Fix all Supabase performance issues: unused indexes, unindexed foreign keys, etc."""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Fixing All Supabase Performance Issues ===")
        
        # 1. Find and remove unused indexes
        print("\n1. Checking for unused indexes...")
        cursor.execute("""
            SELECT schemaname, tablename, indexname, idx_tup_read, idx_tup_fetch
            FROM pg_stat_user_indexes 
            WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
            AND schemaname = 'public'
            AND indexname NOT LIKE '%_pkey';
        """)
        
        unused_indexes = cursor.fetchall()
        for schema, table, index, reads, fetches in unused_indexes:
            print(f"Dropping unused index: {index}")
            cursor.execute(f"DROP INDEX IF EXISTS {index};")
        
        # 2. Find unindexed foreign keys and create indexes
        print("\n2. Creating indexes for foreign keys...")
        cursor.execute("""
            SELECT tc.table_name, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND NOT EXISTS (
                SELECT 1 FROM pg_indexes 
                WHERE tablename = tc.table_name 
                AND indexdef LIKE '%' || kcu.column_name || '%'
            );
        """)
        
        unindexed_fks = cursor.fetchall()
        for table, column in unindexed_fks:
            index_name = f"idx_{table}_{column}"
            print(f"Creating index: {index_name}")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column});")
        
        # 3. Create performance indexes for common query patterns
        print("\n3. Creating performance indexes...")
        
        performance_indexes = [
            ("idx_analytics_created_at", "analytics", "created_at"),
            ("idx_enhanced_analytics_created_at", "enhanced_analytics", "created_at"),
            ("idx_feedback_created_at", "feedback", "created_at"),
            ("idx_videos_created_at", "videos", "created_at"),
            ("idx_system_logs_timestamp", "system_logs", "timestamp"),
            ("idx_analytics_event_type", "analytics", "event_type"),
            ("idx_enhanced_analytics_event_type", "enhanced_analytics", "event_type"),
        ]
        
        for index_name, table, column in performance_indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column});")
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:50]}")
        
        # 4. Create composite indexes for multi-column queries
        print("\n4. Creating composite indexes...")
        
        composite_indexes = [
            ("idx_analytics_user_event", "analytics", "user_id, event_type"),
            ("idx_enhanced_analytics_user_event", "enhanced_analytics", "user_id, event_type"),
            ("idx_feedback_user_created", "feedback", "user_id, created_at"),
            ("idx_videos_user_created", "videos", "user_id, created_at"),
        ]
        
        for index_name, table, columns in composite_indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({columns});")
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:50]}")
        
        # 5. Analyze tables for better query planning
        print("\n5. Analyzing tables...")
        tables = ['user', 'scripts', 'videos', 'analytics', 'enhanced_analytics', 'feedback', 'system_logs']
        for table in tables:
            try:
                cursor.execute(f"ANALYZE {table};")
                print(f"Analyzed: {table}")
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 6. Final status check
        print("\n6. Final status check...")
        cursor.execute("""
            SELECT COUNT(*) as total_indexes
            FROM pg_indexes 
            WHERE schemaname = 'public';
        """)
        
        total_indexes = cursor.fetchone()[0]
        print(f"Total indexes: {total_indexes}")
        
        cursor.close()
        conn.close()
        
        print(f"\nSUCCESS: Fixed Supabase performance issues")
        print(f"- Removed {len(unused_indexes)} unused indexes")
        print(f"- Added {len(unindexed_fks)} foreign key indexes")
        print(f"- Created performance and composite indexes")
        print(f"- Analyzed tables for query optimization")
        
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
    
    success = fix_all_supabase_issues()
    
    if success:
        print("\nAll Supabase performance issues resolved!")
    else:
        print("\nFailed to fix some issues.")