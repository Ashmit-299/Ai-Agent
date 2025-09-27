#!/usr/bin/env python3
"""
Add performance indexes to optimize Supabase queries
"""

import os
import psycopg2
from dotenv import load_dotenv

def add_performance_indexes(cur):
    """Add indexes for better query performance"""
    
    indexes = [
        # User table indexes
        ('user', 'idx_user_email', 'email'),
        ('user', 'idx_user_username', 'username'),
        
        # Content table indexes  
        ('content', 'idx_content_uploader', 'uploader_id'),
        ('content', 'idx_content_type', 'content_type'),
        ('content', 'idx_content_uploaded_at', 'uploaded_at'),
        
        # Feedback table indexes
        ('feedback', 'idx_feedback_content', 'content_id'),
        ('feedback', 'idx_feedback_user', 'user_id'),
        ('feedback', 'idx_feedback_timestamp', 'timestamp'),
        
        # Analytics table indexes
        ('analytics', 'idx_analytics_user', 'user_id'),
        ('analytics', 'idx_analytics_content', 'content_id'),
        ('analytics', 'idx_analytics_timestamp', 'timestamp'),
        ('analytics', 'idx_analytics_event_type', 'event_type'),
        
        # Enhanced analytics indexes
        ('enhanced_analytics', 'idx_enhanced_analytics_user', 'user_id'),
        ('enhanced_analytics', 'idx_enhanced_analytics_content', 'content_id'),
        ('enhanced_analytics', 'idx_enhanced_analytics_timestamp', 'timestamp'),
        ('enhanced_analytics', 'idx_enhanced_analytics_event_type', 'event_type'),
        
        # Script table indexes
        ('script', 'idx_script_content', 'content_id'),
        ('script', 'idx_script_user', 'user_id'),
        ('script', 'idx_script_created_at', 'created_at'),
    ]
    
    print("Adding performance indexes...")
    
    for table, index_name, column in indexes:
        try:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            if not cur.fetchone()[0]:
                continue
                
            # Check if column exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s 
                    AND column_name = %s
                );
            """, (table, column))
            
            if not cur.fetchone()[0]:
                continue
                
            # Create index if it doesn't exist
            cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON public."{table}" ({column});
            ''')
            
            print(f"  Created index {index_name} on {table}.{column}")
            
        except Exception as e:
            print(f"  Error creating index {index_name}: {e}")

def add_composite_indexes(cur):
    """Add composite indexes for complex queries"""
    
    composite_indexes = [
        # Analytics queries by user and time
        ('analytics', 'idx_analytics_user_timestamp', ['user_id', 'timestamp']),
        ('enhanced_analytics', 'idx_enhanced_analytics_user_timestamp', ['user_id', 'timestamp']),
        
        # Content queries by uploader and time
        ('content', 'idx_content_uploader_uploaded', ['uploader_id', 'uploaded_at']),
        
        # Feedback queries by content and time
        ('feedback', 'idx_feedback_content_timestamp', ['content_id', 'timestamp']),
    ]
    
    print("Adding composite indexes...")
    
    for table, index_name, columns in composite_indexes:
        try:
            # Check if table exists
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            if not cur.fetchone()[0]:
                continue
                
            # Create composite index
            columns_str = ', '.join(columns)
            cur.execute(f'''
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON public."{table}" ({columns_str});
            ''')
            
            print(f"  Created composite index {index_name} on {table}")
            
        except Exception as e:
            print(f"  Error creating composite index {index_name}: {e}")

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found or not PostgreSQL")
        return False
    
    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Add single column indexes
        add_performance_indexes(cur)
        
        # Add composite indexes
        add_composite_indexes(cur)
        
        conn.commit()
        
        # Show final index count
        cur.execute("""
            SELECT schemaname, tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname NOT LIKE '%_pkey'
            ORDER BY tablename, indexname;
        """)
        
        results = cur.fetchall()
        print(f"\nTotal custom indexes created: {len(results)}")
        
        cur.close()
        conn.close()
        
        print("Performance indexes added successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Supabase Performance Indexes")
    print("=" * 30)
    main()