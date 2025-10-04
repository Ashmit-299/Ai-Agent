#!/usr/bin/env python3
"""
Fix user_id issue - the user_id has a space in it which is invalid
"""
import os
from dotenv import load_dotenv

load_dotenv()

def fix_user_id():
    """Fix the user_id format"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check the actual user_id for user 'ashm'
        cur.execute('SELECT user_id, username FROM "user" WHERE username = %s', ('ashm',))
        result = cur.fetchone()
        
        if result:
            actual_user_id = result[0]
            username = result[1]
            print(f"Found user: {username}")
            print(f"Actual user_id: '{actual_user_id}'")
            print(f"User_id length: {len(actual_user_id)}")
            print(f"Has space: {' ' in actual_user_id}")
            
            # If user_id has a space, fix it
            if ' ' in actual_user_id:
                new_user_id = actual_user_id.replace(' ', '')
                print(f"\nFixing user_id: '{actual_user_id}' -> '{new_user_id}'")
                
                # Update user_id
                cur.execute('UPDATE "user" SET user_id = %s WHERE user_id = %s', (new_user_id, actual_user_id))
                conn.commit()
                print(f"[OK] User_id fixed!")
                
                # Verify
                cur.execute('SELECT user_id FROM "user" WHERE username = %s', ('ashm',))
                verified_id = cur.fetchone()[0]
                print(f"Verified new user_id: '{verified_id}'")
            else:
                print("\n[OK] User_id is already correct (no space)")
        else:
            print("[ERROR] User 'ashm' not found")
        
        cur.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to fix user_id: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Fixing User ID Issue")
    print("="*60)
    print()
    
    fix_user_id()
    
    print("\n" + "="*60)
    print("Next steps:")
    print("1. Restart the server")
    print("2. Login again to get a new token with correct user_id")
    print("3. Test the feedback endpoint")
    print("="*60)
