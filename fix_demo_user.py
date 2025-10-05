#!/usr/bin/env python3
"""
Fix Demo User Authentication
Creates proper demo user and tests authentication
"""

import os
import sys
import sqlite3
import bcrypt
import requests
from dotenv import load_dotenv

def create_demo_user():
    """Create demo user in database"""
    print("Creating demo user...")
    
    # Load environment
    load_dotenv()
    
    try:
        # Connect to database
        db_path = "test_ai_agent.db"
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        
        # Create users table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Hash demo password
        password = "demo1234"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert demo user
        cur.execute("""
            INSERT OR REPLACE INTO users (user_id, username, email, password_hash, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("demo_user_001", "demo", "demo@example.com", password_hash, "user", 1))
        
        conn.commit()
        conn.close()
        
        print("Demo user created successfully")
        return True
        
    except Exception as e:
        print(f"Error creating demo user: {e}")
        return False

def test_authentication():
    """Test authentication flow"""
    print("Testing authentication...")
    
    try:
        # Get demo credentials
        response = requests.get("http://localhost:9000/demo-login", timeout=5)
        if response.status_code != 200:
            print(f"Demo login endpoint failed: {response.status_code}")
            return False
        
        demo_data = response.json()
        username = demo_data.get('username', 'demo')
        password = demo_data.get('password', 'demo1234')
        
        print(f"Using credentials: {username}/{password}")
        
        # Test login
        login_response = requests.post(
            "http://localhost:9000/users/login",
            data={"username": username, "password": password},
            timeout=10
        )
        
        print(f"Login response status: {login_response.status_code}")
        if login_response.status_code == 200:
            token_data = login_response.json()
            print(f"Login successful! Token type: {token_data.get('token_type', 'unknown')}")
            return True
        else:
            print(f"Login failed: {login_response.text}")
            return False
            
    except Exception as e:
        print(f"Authentication test error: {e}")
        return False

def main():
    """Main function"""
    print("Fixing Demo User Authentication")
    print("=" * 40)
    
    success = True
    
    if not create_demo_user():
        success = False
    
    if not test_authentication():
        success = False
    
    if success:
        print("\nDemo user authentication fixed!")
        return True
    else:
        print("\nDemo user authentication still has issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)