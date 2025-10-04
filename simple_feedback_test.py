#!/usr/bin/env python3
"""
Simple feedback test - bypass the endpoint and test database directly
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

def test_feedback_direct():
    """Test feedback submission directly to database"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Test data
        content_id = "9a2b35e14d7c_30df5d"
        user_id = "544951686 0f9"
        rating = 5
        comment = "great"
        timestamp = time.time()
        reward = (rating - 3) / 2.0
        event_type = 'like'
        
        print("Testing direct feedback insertion...")
        print(f"Content ID: {content_id}")
        print(f"User ID: {user_id}")
        print(f"Rating: {rating}")
        print(f"Comment: {comment}")
        
        # Insert feedback
        cur.execute("""
            INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            content_id, user_id, event_type, 0, reward, rating, comment, timestamp, "127.0.0.1"
        ))
        
        feedback_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"\n[SUCCESS] Feedback inserted with ID: {feedback_id}")
        
        # Verify insertion
        cur.execute("SELECT * FROM feedback WHERE id = %s", (feedback_id,))
        result = cur.fetchone()
        
        print("\nVerification:")
        print(f"  ID: {result[0]}")
        print(f"  Content ID: {result[1]}")
        print(f"  User ID: {result[2]}")
        print(f"  Event Type: {result[3]}")
        print(f"  Rating: {result[6]}")
        print(f"  Comment: {result[7]}")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Direct feedback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Direct Feedback Database Test")
    print("="*60)
    print()
    
    success = test_feedback_direct()
    
    print("\n" + "="*60)
    if success:
        print("Database insertion works!")
        print("The issue is in the endpoint code, not the database.")
        print("\nLikely causes:")
        print("1. Exception being caught and not re-raised")
        print("2. Missing import or module")
        print("3. RL agent or observability error")
    else:
        print("Database insertion failed!")
        print("Check database connection and table structure.")
    print("="*60)
