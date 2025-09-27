#!/usr/bin/env python3
"""
Final cleanup - handle the last duplicate index properly
"""

import os
import psycopg2
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found")
        return False
    
    try:
        print("Final Index Cleanup")
        print("=" * 20)
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # The user_username_key is a constraint index, so we drop the regular index instead
        print("Removing non-constraint duplicate index...")
        
        try:
            cur.execute('DROP INDEX IF EXISTS public."idx_user_username";')
            print("  Dropped: idx_user_username (keeping constraint index user_username_key)")
        except Exception as e:
            print(f"  Error: {e}")
        
        conn.commit()
        
        # Final verification
        cur.execute("""
            SELECT 
                tablename,
                COUNT(*) as index_count
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND indexname NOT LIKE '%_pkey'
            GROUP BY tablename
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        total = sum(count for _, count in results)
        
        print(f"\nFinal Index Count:")
        for table, count in results:
            print(f"  {table}: {count}")
        
        print(f"Total: {total}")
        
        # Check for any remaining duplicates
        cur.execute("""
            WITH index_columns AS (
                SELECT 
                    tablename,
                    indexname,
                    regexp_replace(indexdef, '.*USING [^(]*\\(([^)]*)\\).*', '\\1') as columns
                FROM pg_indexes 
                WHERE schemaname = 'public'
                AND indexname NOT LIKE '%_pkey'
            ),
            duplicates AS (
                SELECT 
                    tablename,
                    columns,
                    COUNT(*) as dup_count
                FROM index_columns
                GROUP BY tablename, columns
                HAVING COUNT(*) > 1
            )
            SELECT COUNT(*) FROM duplicates;
        """)
        
        dup_count = cur.fetchone()[0]
        
        status = "RESOLVED" if dup_count == 0 else f"STILL HAS {dup_count} DUPLICATES"
        print(f"\nDuplicate Index Status: {status}")
        
        cur.close()
        conn.close()
        
        return dup_count == 0
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    main()