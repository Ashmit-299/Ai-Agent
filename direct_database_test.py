#!/usr/bin/env python3
"""
Direct database connection test
"""

import os
import time
from dotenv import load_dotenv
load_dotenv()

def test_direct_database():
    """Test direct database connection and upload simulation"""
    
    print("Direct Database Connection Test")
    print("=" * 50)
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("[ERROR] No DATABASE_URL configured in .env")
        return False
    
    if "postgresql" not in DATABASE_URL:
        print("[ERROR] DATABASE_URL is not PostgreSQL")
        return False
    
    print(f"[OK] DATABASE_URL configured: {DATABASE_URL[:50]}...")
    
    try:
        import psycopg2
        print("[OK] psycopg2 module available")
        
        # Test connection
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("[OK] Connected to Supabase")
        
        # Test basic query
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        print(f"[OK] Database version: {version[:50]}...")
        
        # Check if content table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'content'
            )
        """)
        table_exists = cur.fetchone()[0]
        print(f"[OK] Content table exists: {table_exists}")
        
        if table_exists:
            # Get current content count
            cur.execute("SELECT COUNT(*) FROM content")
            count_before = cur.fetchone()[0]
            print(f"[OK] Current content count: {count_before}")
            
            # Test insert
            test_content_id = f"test_direct_{int(time.time())}"
            cur.execute("""
                INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                test_content_id, 'test_user', 'Direct Test Upload', 'Testing direct database insert',
                '/test/path', 'text/plain', 100, time.time(), 0.8, '', 0, 0, 0
            ))
            
            # Verify insert
            cur.execute("SELECT content_id, title FROM content WHERE content_id = %s", (test_content_id,))
            result = cur.fetchone()
            
            if result:
                print(f"[OK] Test insert successful: {result[0]} - {result[1]}")
                
                # Get new count
                cur.execute("SELECT COUNT(*) FROM content")
                count_after = cur.fetchone()[0]
                print(f"[OK] New content count: {count_after}")
                
                # Clean up test data
                cur.execute("DELETE FROM content WHERE content_id = %s", (test_content_id,))
                print(f"[OK] Test data cleaned up")
                
            else:
                print("[ERROR] Test insert failed - no data found")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("[SUCCESS] Database connection and operations working!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_direct_database()
    if success:
        print("\n✅ Database is working - upload endpoint should save data")
    else:
        print("\n❌ Database issues found - upload endpoint won't save data")