#!/usr/bin/env python3
"""
Fix demo user credentials for login
"""

import sqlite3
import time
from passlib.context import CryptContext

def fix_demo_user():
    """Create/update demo user with proper bcrypt hash"""
    try:
        # Create password context
        pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        demo_hash = pwd_context.hash('demo1234')
        
        # Connect to database
        conn = sqlite3.connect('data.db')
        with conn:
            cur = conn.cursor()
            
            # Create user table if not exists
            cur.execute('''CREATE TABLE IF NOT EXISTS user (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT,
                email TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                created_at REAL
            )''')
            
            # Check if demo user exists
            cur.execute('SELECT user_id, password_hash FROM user WHERE username=?', ('demo',))
            existing_user = cur.fetchone()
            
            if existing_user:
                # Update existing user's password
                cur.execute('UPDATE user SET password_hash=? WHERE username=?', (demo_hash, 'demo'))
                print(f"Updated existing demo user: {existing_user[0]}")
            else:
                # Create new demo user
                cur.execute('INSERT INTO user(user_id, username, password_hash, email, email_verified, created_at) VALUES (?,?,?,?,?,?)',
                           ('demo001', 'demo', demo_hash, 'demo@example.com', True, time.time()))
                print("Created new demo user: demo001")
            
            # Verify the password works
            cur.execute('SELECT password_hash FROM user WHERE username=?', ('demo',))
            stored_hash = cur.fetchone()[0]
            
            if pwd_context.verify('demo1234', stored_hash):
                print("✅ Password verification: SUCCESS")
                print("✅ Demo credentials: username='demo', password='demo1234'")
                return True
            else:
                print("❌ Password verification: FAILED")
                return False
                
        conn.close()
        
    except Exception as e:
        print(f"❌ Error fixing demo user: {e}")
        return False

if __name__ == "__main__":
    print("Fixing demo user credentials...")
    success = fix_demo_user()
    if success:
        print("\n🎉 Demo user is ready for login!")
        print("You can now use POST /users/login with:")
        print("  username: demo")
        print("  password: demo1234")
    else:
        print("\n💥 Failed to fix demo user")