#!/usr/bin/env python3
"""
Test direct database insert to verify the fix
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

def test_direct_insert():
    """Test direct feedback insertion with all required fields"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Test data
        content_id = "9a2b35e14d7c_30df5d"
        user_id = "5449516860f9"  # Correct user_id without space
        rating = 5
        comment = "great"
        reward = (rating - 3) / 2.0
        event_type = 'like'
        timestamp = time.time()
        
        print("Testing direct feedback insertion with all fields...")
        print(f"Content ID: {content_id}")
        print(f"User ID: {user_id}")
        print(f"Rating: {rating}")
        print(f"Watch time: 0 (default)")
        
        # Insert with all required fields
        cur.execute("""
            INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, rating, comment, reward, timestamp, ip_address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            content_id, user_id, event_type, 0, rating, comment, reward, timestamp, "127.0.0.1"
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
        print(f"  Watch Time: {result[4]}")
        print(f"  Reward: {result[5]}")
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
    print("Direct Feedback Database Test - Fixed Version")
    print("="*60)
    print()
    
    success = test_direct_insert()
    
    print("\n" + "="*60)
    if success:
        print("✓ Database insertion works!")
        print("The feedback endpoint should now work.")
        print("\nRestart server and test:")
        print("curl -X POST http://localhost:9000/feedback \\")
        print('  -H "Authorization: Bearer YOUR_TOKEN" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"content_id": "9a2b35e14d7c_30df5d", "rating": 5, "comment": "great"}\'')
    else:
        print("✗ Database insertion failed!")
    print("="*60)