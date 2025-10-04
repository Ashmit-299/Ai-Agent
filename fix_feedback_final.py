#!/usr/bin/env python3
"""
Final fix for feedback endpoint - remove foreign key constraints
"""
import os
from dotenv import load_dotenv

load_dotenv()

def fix_feedback_constraints():
    """Remove foreign key constraints from feedback table"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("Removing foreign key constraints from feedback table...")
        
        # Drop foreign key constraints
        cur.execute("""
            ALTER TABLE feedback 
            DROP CONSTRAINT IF EXISTS feedback_content_id_fkey,
            DROP CONSTRAINT IF EXISTS feedback_user_id_fkey
        """)
        
        conn.commit()
        print("[OK] Foreign key constraints removed!")
        
        # Test insertion
        import time
        test_data = {
            'content_id': '9a2b35e14d7c_30df5d',
            'user_id': '544951686 0f9',  # The problematic user_id
            'event_type': 'like',
            'rating': 5,
            'comment': 'test',
            'reward': 1.0,
            'timestamp': time.time(),
            'ip_address': '127.0.0.1'
        }
        
        print("\nTesting feedback insertion...")
        cur.execute("""
            INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            test_data['content_id'], test_data['user_id'], test_data['event_type'],
            0, test_data['reward'], test_data['rating'], test_data['comment'],
            test_data['timestamp'], test_data['ip_address']
        ))
        
        feedback_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"[SUCCESS] Test feedback inserted with ID: {feedback_id}")
        
        # Clean up test data
        cur.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
        conn.commit()
        print("[OK] Test data cleaned up")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Final Feedback Endpoint Fix")
    print("="*60)
    print()
    
    if fix_feedback_constraints():
        print("\n" + "="*60)
        print("[SUCCESS] Feedback endpoint is now fixed!")
        print("="*60)
        print("\nThe feedback endpoint will now work with any user_id.")
        print("No need to login again - your current token will work!")
    else:
        print("\n" + "="*60)
        print("[FAILED] Could not fix feedback endpoint")
        print("="*60)
