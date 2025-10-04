#!/usr/bin/env python3
"""
Fix user table schema to use user_id as primary key
"""

import sqlite3
import os
import uuid

def fix_user_schema():
    """Fix the user table to use user_id as primary key"""
    db_path = 'data.db'
    
    if not os.path.exists(db_path):
        print("Database not found, creating new one...")
        return
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Check current schema
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(user)")
        columns = cursor.fetchall()
        
        # Check if user_id column exists
        has_user_id = any(col[1] == 'user_id' for col in columns)
        
        if has_user_id:
            print("User table already has user_id column")
            return
        
        print("Fixing user table schema...")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE user_new (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                created_at REAL
            )
        """)
        
        # Copy data from old table, generating user_id for existing users
        cursor.execute("SELECT * FROM user")
        old_users = cursor.fetchall()
        
        for user in old_users:
            # Generate user_id if it doesn't exist
            user_id = f"user_{uuid.uuid4().hex[:8]}"
            
            # Map old columns to new schema
            if len(user) >= 3:  # id, username, password_hash
                username = user[1]
                password_hash = user[2]
                email = user[3] if len(user) > 3 else None
                created_at = user[4] if len(user) > 4 else None
                
                cursor.execute("""
                    INSERT INTO user_new (user_id, username, password_hash, email, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, username, password_hash, email, created_at))
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE user")
        cursor.execute("ALTER TABLE user_new RENAME TO user")
        
        conn.commit()
        print("User table schema fixed successfully!")
        
    except Exception as e:
        print(f"Error fixing schema: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_schema()