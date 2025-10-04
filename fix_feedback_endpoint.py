#!/usr/bin/env python3
"""
Fix feedback endpoint error
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Test feedback endpoint
def test_feedback():
    """Test feedback submission"""
    import requests
    import json
    
    # Get token first
    login_url = "http://localhost:9000/users/login"
    login_data = {
        "username": "ashm",
        "password": "your_password_here"  # Replace with actual password
    }
    
    print("Testing feedback endpoint...")
    print("1. Login to get token...")
    
    # For testing, use a sample token or get from login
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2htIiwidXNlcl9pZCI6IjU0NDk1MTY4NjBmOSIsImV4cCI6MTc1OTY1NDE1NCwiaWF0IjoxNzU5NTY3NzU0LCJ0eXBlIjoiYWNjZXNzIiwianRpIjoiSWk5b0lsY2dzbllRdjRnUG03eU1VUSJ9.Iyi2mpL-kOtUTc8ExWRsDFd_4PV-I21jZIEFwcKqW24"
    
    # Test feedback
    feedback_url = "http://localhost:9000/feedback"
    feedback_data = {
        "content_id": "9a2b35e14d7c_30df5d",
        "rating": 5,
        "comment": "great"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("2. Submitting feedback...")
    try:
        response = requests.post(feedback_url, json=feedback_data, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("\nError detected! Checking database...")
            check_database()
    except Exception as e:
        print(f"Request failed: {e}")

def check_database():
    """Check if feedback table exists and has correct structure"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if feedback table exists
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'feedback'
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("\nFeedback table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check if content exists
        cur.execute("SELECT content_id, title FROM content WHERE content_id = '9a2b35e14d7c_30df5d'")
        content = cur.fetchone()
        
        if content:
            print(f"\nContent found: {content[1]}")
        else:
            print("\nContent NOT found! This might be the issue.")
            print("Creating test content...")
            
            # Create test content
            import time
            cur.execute("""
                INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (content_id) DO NOTHING
            """, (
                '9a2b35e14d7c_30df5d', '544951686 0f9', 'Test Content', 'Test Description',
                '/test/path.mp4', 'video/mp4', time.time(), 0.8, '["test"]', 0, 0, 0
            ))
            conn.commit()
            print("Test content created!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Database check failed: {e}")

if __name__ == "__main__":
    check_database()
    print("\n" + "="*60)
    print("Database check complete!")
    print("="*60)
    print("\nTo test feedback endpoint:")
    print("1. Make sure server is running: python scripts/start_server.py")
    print("2. Get a valid token by logging in")
    print("3. Use the /feedback endpoint with valid content_id")
