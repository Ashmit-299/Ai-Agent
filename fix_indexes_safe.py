#!/usr/bin/env python3
"""
Safe fix for duplicate indexes - only remove non-constraint indexes
"""

import os
import psycopg2
from dotenv import load_dotenv

def get_safe_to_drop_indexes(cur):
    """Get indexes that are safe to drop (not supporting constraints)"""
    
    cur.execute("""
        SELECT 
            i.schemaname,
            i.tablename,
            i.indexname,
            i.indexdef,
            CASE WHEN c.conname IS NOT NULL THEN true ELSE false END as supports_constraint
        FROM pg_indexes i
        LEFT JOIN pg_constraint c ON c.conname = i.indexname
        WHERE i.schemaname = 'public'
        AND i.indexname NOT LIKE '%_pkey'
        ORDER BY i.tablename, i.indexname;
    """)
    
    return cur.fetchall()

def find_redundant_indexes(indexes):
    """Find truly redundant indexes (same table, same columns)"""
    
    # Group by table and column pattern
    table_columns = {}
    redundant = []
    
    for schema, table, index_name, index_def, has_constraint in indexes:
        if has_constraint:
            continue  # Skip constraint-supporting indexes
            
        # Extract columns from index definition
        if 'USING btree (' in index_def:
            columns = index_def.split('USING btree (')[1].split(')')[0].strip()
            
            key = f"{table}:{columns}"
            if key in table_columns:
                redundant.append((table, index_name, columns, table_columns[key]))
            else:
                table_columns[key] = index_name
    
    return redundant

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Safe Duplicate Index Fix")
        print("=" * 25)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get all indexes with constraint info
        indexes = get_safe_to_drop_indexes(cur)
        
        print(f"Total indexes found: {len(indexes)}")
        
        # Find redundant indexes
        redundant = find_redundant_indexes(indexes)
        
        print(f"Redundant indexes to remove: {len(redundant)}")
        
        # Remove redundant indexes
        removed_count = 0
        for table, index_name, columns, original in redundant:
            try:
                cur.execute(f'DROP INDEX IF EXISTS public."{index_name}";')
                print(f"  Dropped: {index_name} (duplicate of {original})")
                removed_count += 1
            except Exception as e:
                print(f"  Skipped {index_name}: {e}")
        
        # Remove obviously redundant patterns
        print("\nRemoving pattern-based duplicates...")
        
        # Get remaining indexes
        cur.execute("""
            SELECT indexname, tablename
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
            AND indexname NOT IN (
                SELECT conname FROM pg_constraint WHERE conname IS NOT NULL
            )
            ORDER BY tablename, indexname;
        """)
        
        remaining = cur.fetchall()
        
        # Remove indexes with similar patterns
        patterns_to_remove = []
        seen_patterns = set()
        
        for index_name, table in remaining:
            # Check for common duplicate patterns
            base_patterns = [
                f"ix_{table}_",
                f"idx_{table}_", 
                f"{table}_"
            ]
            
            for pattern in base_patterns:
                if index_name.startswith(pattern):
                    # Extract the column part
                    col_part = index_name.replace(pattern, "")
                    key = f"{table}:{col_part}"
                    
                    if key in seen_patterns:
                        patterns_to_remove.append(index_name)
                    else:
                        seen_patterns.add(key)
        
        # Remove pattern duplicates
        for index_name in patterns_to_remove:
            try:
                cur.execute(f'DROP INDEX IF EXISTS public."{index_name}";')
                print(f"  Dropped pattern duplicate: {index_name}")
                removed_count += 1
            except Exception as e:
                print(f"  Skipped {index_name}: {e}")
        
        conn.commit()
        
        # Final count
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey';
        """)
        
        final_count = cur.fetchone()[0]
        
        print(f"\nSummary:")
        print(f"  Indexes removed: {removed_count}")
        print(f"  Final index count: {final_count}")
        print("Duplicate index warnings should be resolved!")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()