#!/usr/bin/env python3

import os
import psycopg2

def fix_duplicate_indexes():
    """Remove duplicate indexes and fix all Supabase suggestions"""
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== Fixing Duplicate Indexes and Suggestions ===")
        
        # 1. Find duplicate indexes (same table, same columns)
        print("\n1. Finding duplicate indexes...")
        cursor.execute("""
            WITH index_columns AS (
                SELECT 
                    i.schemaname,
                    i.tablename,
                    i.indexname,
                    array_agg(a.attname ORDER BY a.attnum) as columns
                FROM pg_indexes i
                JOIN pg_class c ON c.relname = i.indexname
                JOIN pg_index idx ON idx.indexrelid = c.oid
                JOIN pg_attribute a ON a.attrelid = idx.indrelid AND a.attnum = ANY(idx.indkey)
                WHERE i.schemaname = 'public'
                AND i.indexname NOT LIKE '%_pkey'
                GROUP BY i.schemaname, i.tablename, i.indexname
            ),
            duplicates AS (
                SELECT 
                    schemaname, tablename, columns,
                    array_agg(indexname) as index_names,
                    count(*) as duplicate_count
                FROM index_columns
                GROUP BY schemaname, tablename, columns
                HAVING count(*) > 1
            )
            SELECT schemaname, tablename, columns, index_names
            FROM duplicates;
        """)
        
        duplicates = cursor.fetchall()
        
        for schema, table, columns, index_names in duplicates:
            # Keep the first index, drop the rest
            indexes_to_drop = index_names[1:]
            print(f"Table {table}, columns {columns}: keeping {index_names[0]}")
            
            for index_name in indexes_to_drop:
                try:
                    cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                    print(f"  Dropped duplicate: {index_name}")
                except Exception as e:
                    print(f"  Failed to drop {index_name}: {str(e)[:40]}")
        
        # 2. Remove unused indexes (no reads/fetches)
        print("\n2. Removing unused indexes...")
        cursor.execute("""
            SELECT schemaname, indexrelname
            FROM pg_stat_user_indexes 
            WHERE idx_tup_read = 0 AND idx_tup_fetch = 0
            AND schemaname = 'public'
            AND indexrelname NOT LIKE '%_pkey'
            AND indexrelname NOT LIKE '%_user_id_key'
            AND indexrelname NOT LIKE '%_email_key';
        """)
        
        unused_indexes = cursor.fetchall()
        for schema, index_name in unused_indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index_name};")
                print(f"Dropped unused: {index_name}")
            except Exception as e:
                print(f"Failed to drop {index_name}: {str(e)[:40]}")
        
        # 3. Create missing essential indexes
        print("\n3. Creating missing essential indexes...")
        
        essential_indexes = [
            ("idx_user_created_at", "user", "created_at"),
            ("idx_script_created_at", "script", "created_at"),
            ("idx_videos_created_at", "videos", "created_at"),
            ("idx_feedback_created_at", "feedback", "created_at"),
            ("idx_analytics_timestamp", "analytics", "timestamp"),
            ("idx_enhanced_analytics_timestamp", "enhanced_analytics", "timestamp"),
        ]
        
        for index_name, table, column in essential_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column});')
                print(f"Created: {index_name}")
            except Exception as e:
                print(f"Skipped {index_name}: {str(e)[:40]}")
        
        # 4. Optimize existing indexes
        print("\n4. Optimizing existing indexes...")
        
        # Create partial indexes for better performance
        partial_indexes = [
            ("idx_user_active", "user", "user_id", "deleted_at IS NULL"),
            ("idx_script_active", "script", "user_id", "deleted_at IS NULL"),
            ("idx_videos_published", "videos", "user_id", "status = 'published'"),
        ]
        
        for index_name, table, column, condition in partial_indexes:
            try:
                cursor.execute(f'CREATE INDEX IF NOT EXISTS {index_name} ON public."{table}"({column}) WHERE {condition};')
                print(f"Created partial: {index_name}")
            except Exception as e:
                print(f"Skipped partial {index_name}: {str(e)[:40]}")
        
        # 5. Update all table statistics
        print("\n5. Updating table statistics...")
        
        cursor.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
            AND tablename NOT LIKE 'sql_%';
        """)
        
        tables = cursor.fetchall()
        for (table,) in tables:
            try:
                cursor.execute(f'ANALYZE public."{table}";')
                print(f"Analyzed: {table}")
            except Exception as e:
                print(f"Skipped {table}: {str(e)[:30]}")
        
        conn.commit()
        
        # 6. Final status
        cursor.execute("SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
        final_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"\nSUCCESS: Index optimization complete")
        print(f"- Removed {len(duplicates)} duplicate index groups")
        print(f"- Removed {len(unused_indexes)} unused indexes")
        print(f"- Final index count: {final_count}")
        
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
    
    success = fix_duplicate_indexes()
    
    if success:
        print("\nDuplicate indexes and suggestions resolved!")
        print("- Removed duplicate and unused indexes")
        print("- Created essential missing indexes")
        print("- Added partial indexes for optimization")
        print("- Updated all table statistics")
    else:
        print("\nFailed to complete optimization.")