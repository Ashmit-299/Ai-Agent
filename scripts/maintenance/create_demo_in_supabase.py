#!/usr/bin/env python3
"""
Create demo user in main Supabase database
"""

import time
from ..core.database import DatabaseManager
from ..app.security import PasswordManager

def create_demo_in_supabase():
    """Create demo user in main Supabase database"""
    try:
        db = DatabaseManager()
        
        # Check if demo user already exists
        existing_user = db.get_user_by_username('demo')
        if existing_user:
            print(f"Demo user already exists in Supabase: {existing_user.user_id}")
            return True
        
        # Create demo user with proper bcrypt hash
        demo_hash = PasswordManager.hash_password('demo1234')
        
        user_data = {
            'user_id': 'demo001',
            'username': 'demo',
            'password_hash': demo_hash,
            'email': 'demo@example.com',
            'email_verified': True,
            'created_at': time.time()
        }
        
        # Create user in Supabase
        new_user = db.create_user(user_data)
        print(f"Demo user created in Supabase: {new_user.user_id}")
        
        # Verify user can be found
        verify_user = db.get_user_by_username('demo')
        if verify_user and PasswordManager.verify_password('demo1234', verify_user.password_hash):
            print("SUCCESS: Demo user created and password verified in Supabase")
            print("Credentials: username=demo, password=demo1234")
            return True
        else:
            print("FAILED: Could not verify demo user in Supabase")
            return False
            
    except Exception as e:
        print(f"Error creating demo user in Supabase: {e}")
        return False

if __name__ == "__main__":
    print("Creating demo user in main Supabase database...")
    success = create_demo_in_supabase()
    if success:
        print("\nDemo user is ready in Supabase database!")
    else:
        print("\nFailed to create demo user in Supabase")