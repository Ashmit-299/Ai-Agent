#!/usr/bin/env python3
"""
Final verification - check for remaining duplicate indexes
"""

import os
import psycopg2
from dotenv import load_dotenv

def analyze_final_indexes(cur):
    """Analyze final index state"""
    
    cur.execute("""
        SELECT 
            tablename,
            indexname,
            indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        AND indexname NOT LIKE '%_pkey'
        ORDER BY tablename, indexname;
    """)
    
    indexes = cur.fetchall()
    
    print("Final Index Analysis:")
    print("=" * 30)
    
    # Group by table
    table_indexes = {}
    for table, index_name, index_def in indexes:
        if table not in table_indexes:
            table_indexes[table] = []
        table_indexes[table].append((index_name, index_def))
    
    total_indexes = 0
    for table, idx_list in table_indexes.items():
        print(f"\n{table.upper()}:")
        for idx_name, idx_def in idx_list:
            # Extract column info
            if 'USING btree (' in idx_def:
                columns = idx_def.split('USING btree (')[1].split(')')[0]
                print(f"  {idx_name}: {columns}")
            else:
                print(f"  {idx_name}: {idx_def}")
            total_indexes += 1
    
    return total_indexes, table_indexes

def check_for_duplicates(table_indexes):
    """Check for any remaining duplicates"""
    
    duplicates_found = []
    
    for table, idx_list in table_indexes.items():
        columns_seen = {}
        for idx_name, idx_def in idx_list:
            if 'USING btree (' in idx_def:
                columns = idx_def.split('USING btree (')[1].split(')')[0]
                if columns in columns_seen:
                    duplicates_found.append((table, idx_name, columns, columns_seen[columns]))
                else:
                    columns_seen[columns] = idx_name
    
    return duplicates_found

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Final Index Verification")
        print("=" * 25)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Analyze final state
        total_indexes, table_indexes = analyze_final_indexes(cur)
        
        # Check for duplicates
        duplicates = check_for_duplicates(table_indexes)
        
        print(f"\nSUMMARY:")
        print(f"Total Indexes: {total_indexes}")
        print(f"Duplicate Indexes: {len(duplicates)}")
        
        if duplicates:
            print("\nRemaining Duplicates:")
            for table, dup_idx, cols, orig_idx in duplicates:
                print(f"  {table}: {dup_idx} duplicates {orig_idx}")
        else:
            print("\nNo duplicate indexes found!")
        
        # Check constraint indexes
        cur.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes i
            JOIN pg_constraint c ON c.conname = i.indexname
            WHERE i.schemaname = 'public';
        """)
        
        constraint_indexes = cur.fetchone()[0]
        print(f"Constraint Indexes: {constraint_indexes} (protected)")
        
        status = "RESOLVED" if len(duplicates) == 0 else "NEEDS ATTENTION"
        print(f"\nDuplicate Index Warnings: {status}")
        
        cur.close()
        conn.close()
        
        return len(duplicates) == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()