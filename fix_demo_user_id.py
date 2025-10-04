#!/usr/bin/env python3
"""
Fix Demo User ID Format
"""

import os
import uuid
from dotenv import load_dotenv

load_dotenv()

def fix_demo_user():
    """Update demo user to use proper hex ID format"""
    try:
        import psycopg2
        from passlib.context import CryptContext
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Generate new hex ID
        new_user_id = uuid.uuid4().hex[:12]  # 12-char hex like f1b4c70cc30b
        
        # Update demo user ID
        cursor.execute('UPDATE "user" SET user_id = %s WHERE username = %s', (new_user_id, 'demo'))
        
        if cursor.rowcount > 0:
            print(f"[SUCCESS] Demo user ID updated to: {new_user_id}")
        else:
            # Create new demo user with proper ID
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            password_hash = pwd_context.hash("demo1234")
            
            cursor.execute("""
                INSERT INTO "user" (user_id, username, password_hash, email, email_verified, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_user_id, 'demo', password_hash, 'demo@example.com', True, 1640995200))
            
            print(f"[SUCCESS] Demo user created with ID: {new_user_id}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return new_user_id
        
    except Exception as e:
        print(f"[ERROR] Failed to fix demo user: {e}")
        return None

if __name__ == "__main__":
    fix_demo_user()