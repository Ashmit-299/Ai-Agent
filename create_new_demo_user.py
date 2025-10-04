#!/usr/bin/env python3
"""
Create New Demo User with Hex ID
"""

import os
import uuid
import time
from dotenv import load_dotenv

load_dotenv()

def create_new_demo_user():
    """Create new demo user with hex ID format"""
    try:
        import psycopg2
        from passlib.context import CryptContext
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Generate hex ID
        demo_user_id = uuid.uuid4().hex[:12]  # 12-char hex like f1b4c70cc30b
        
        # Check if demo user exists
        cursor.execute('SELECT user_id FROM "user" WHERE username = %s', ('demo',))
        existing = cursor.fetchone()
        
        if existing:
            print(f"[INFO] Demo user exists with ID: {existing[0]}")
            cursor.close()
            conn.close()
            return existing[0]
        
        # Create password hash
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash("demo1234")
        
        # Insert new demo user
        cursor.execute("""
            INSERT INTO "user" (user_id, username, password_hash, email, email_verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (demo_user_id, 'demo', password_hash, 'demo@example.com', True, time.time()))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"[SUCCESS] New demo user created with ID: {demo_user_id}")
        return demo_user_id
        
    except Exception as e:
        print(f"[ERROR] Failed to create demo user: {e}")
        return None

if __name__ == "__main__":
    create_new_demo_user()