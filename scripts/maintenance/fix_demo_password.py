#!/usr/bin/env python3
"""
Fix demo user password with proper bcrypt hashing
"""

import time
from ..core.database import DatabaseManager
from ..app.security import PasswordManager

def fix_demo_password():
    """Fix demo user password with proper bcrypt hash"""
    try:
        print("Fixing demo user password...")
        
        # Create proper bcrypt hash
        demo_password = 'demo1234'
        demo_hash = PasswordManager.hash_password(demo_password)
        print(f"Generated bcrypt hash: {demo_hash[:60]}...")
        
        # Update in Supabase database
        try:
            from sqlmodel import Session, select, update
            from ..core.models import User
            from ..core.database import engine
            
            with Session(engine) as session:
                # Find demo user
                statement = select(User).where(User.username == 'demo')
                demo_user = session.exec(statement).first()
                
                if demo_user:
                    print(f"Found demo user: {demo_user.user_id}")
                    
                    # Update password hash
                    demo_user.password_hash = demo_hash
                    session.add(demo_user)
                    session.commit()
                    session.refresh(demo_user)
                    
                    print("Demo user password updated in Supabase")
                    
                    # Verify the update worked
                    if PasswordManager.verify_password(demo_password, demo_user.password_hash):
                        print("[OK] Password verification successful after update")
                        return True
                    else:
                        print("[FAIL] Password verification still failed")
                        return False
                else:
                    print("[FAIL] Demo user not found in Supabase")
                    return False
                    
        except Exception as supabase_error:
            print(f"Supabase update failed: {supabase_error}")
            
            # Fallback to SQLite
            print("Trying SQLite fallback...")
            import sqlite3
            
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                
                # Check if demo user exists
                cur.execute('SELECT user_id FROM user WHERE username=?', ('demo',))
                existing = cur.fetchone()
                
                if existing:
                    # Update existing user
                    cur.execute('UPDATE user SET password_hash=? WHERE username=?', (demo_hash, 'demo'))
                    print("Updated demo user in SQLite")
                else:
                    # Create new demo user
                    cur.execute('''
                        INSERT INTO user (user_id, username, password_hash, email, email_verified, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', ('demo001', 'demo', demo_hash, 'demo@example.com', True, time.time()))
                    print("Created demo user in SQLite")
            
            conn.close()
            
            # Verify SQLite update
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                cur.execute('SELECT password_hash FROM user WHERE username=?', ('demo',))
                result = cur.fetchone()
            conn.close()
            
            if result and PasswordManager.verify_password(demo_password, result[0]):
                print("[OK] SQLite password verification successful")
                return True
            else:
                print("[FAIL] SQLite password verification failed")
                return False
                
    except Exception as e:
        print(f"Error fixing demo password: {e}")
        return False

if __name__ == "__main__":
    print("=== Fixing Demo User Password ===")
    success = fix_demo_password()
    
    if success:
        print("\n[SUCCESS] Demo user password fixed!")
        print("Credentials: username=demo, password=demo1234")
    else:
        print("\n[FAILED] Could not fix demo user password")