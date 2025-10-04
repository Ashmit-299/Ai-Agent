#!/usr/bin/env python3
"""
Fix foreign key constraint issue for uploads
"""

import os
import time
from dotenv import load_dotenv
load_dotenv()

def fix_foreign_key_constraint():
    """Fix the foreign key constraint by ensuring anonymous user exists"""
    
    print("Fixing Foreign Key Constraint Issue")
    print("=" * 50)
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if anonymous user exists
        cur.execute('SELECT user_id FROM "user" WHERE user_id = %s', ('anonymous',))
        anonymous_exists = cur.fetchone()
        
        if not anonymous_exists:
            print("[INFO] Creating anonymous user for uploads...")
            
            # Create anonymous user
            cur.execute("""
                INSERT INTO "user" (user_id, username, password_hash, email, email_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (
                'anonymous', 'anonymous', 'no_password', 'anonymous@system.local', 
                True, time.time()
            ))
            
            print("[OK] Anonymous user created")
        else:
            print("[OK] Anonymous user already exists")
        
        # Test upload with anonymous user
        test_content_id = f"test_fixed_{int(time.time())}"
        cur.execute("""
            INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_content_id, 'anonymous', 'Test Fixed Upload', 'Testing after fixing foreign key',
            '/test/path', 'text/plain', 100, time.time(), 0.8, '', 0, 0, 0
        ))
        
        # Verify insert
        cur.execute("SELECT content_id, title FROM content WHERE content_id = %s", (test_content_id,))
        result = cur.fetchone()
        
        if result:
            print(f"[OK] Test upload successful: {result[0]} - {result[1]}")
            
            # Clean up test data
            cur.execute("DELETE FROM content WHERE content_id = %s", (test_content_id,))
            print("[OK] Test data cleaned up")
        else:
            print("[ERROR] Test upload still failed")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("[SUCCESS] Foreign key constraint fixed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_foreign_key_constraint()
    if success:
        print("\nForeign key issue fixed - upload endpoint should now work!")
    else:
        print("\nFailed to fix foreign key issue")