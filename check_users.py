#!/usr/bin/env python3
"""
Check existing users and suggest available usernames
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import random

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def get_database_url():
    """Get database URL from environment or use default SQLite"""
    from dotenv import load_dotenv
    load_dotenv()
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        # Default to SQLite
        db_url = "sqlite:///./data/data.db"
    return db_url

def check_existing_users():
    """Check existing users in the database"""
    try:
        db_url = get_database_url()
        print(f"Connecting to database: {db_url.split('@')[0] if '@' in db_url else db_url}")
        
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as session:
            # Check if users table exists (works for both PostgreSQL and SQLite)
            try:
                if 'postgresql' in db_url:
                    # PostgreSQL query
                    result = session.execute(text("SELECT tablename FROM pg_tables WHERE tablename='user'"))
                else:
                    # SQLite query
                    result = session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user'"))
                
                if not result.fetchone():
                    print("Users table does not exist. Run database initialization first.")
                    return []
            except Exception as table_check_error:
                print(f"Could not check table existence: {table_check_error}")
                print("Attempting to query users table directly...")
            
            # Get all users
            result = session.execute(text('SELECT username, email, created_at FROM "user" ORDER BY created_at DESC'))
            users = result.fetchall()
            
            print(f"\nFound {len(users)} existing users:")
            print("-" * 60)
            
            if users:
                for i, user in enumerate(users, 1):
                    print(f"{i:2d}. Username: {user[0]:<15} Email: {user[1]:<25} Created: {user[2]}")
            else:
                print("No users found in database.")
            
            return [user[0] for user in users]
            
    except Exception as e:
        print(f"Error checking users: {e}")
        print("This might mean the database is not initialized or users table doesn't exist.")
        return []

def suggest_usernames(existing_users, base_names=None):
    """Suggest available usernames"""
    if base_names is None:
        base_names = [
            "admin", "user", "test", "demo", "guest", "developer", "manager", 
            "analyst", "creator", "editor", "viewer", "moderator", "support"
        ]
    
    suggestions = []
    
    # Simple base names
    for name in base_names:
        if name not in existing_users:
            suggestions.append(name)
    
    # Numbered variations
    for name in base_names[:5]:  # Only for first 5 base names
        for i in range(1, 10):
            candidate = f"{name}{i}"
            if candidate not in existing_users:
                suggestions.append(candidate)
    
    # Random variations
    suffixes = ["_dev", "_test", "_new", "_2024", "_user", "_admin"]
    for name in base_names[:3]:
        for suffix in suffixes:
            candidate = f"{name}{suffix}"
            if candidate not in existing_users:
                suggestions.append(candidate)
    
    return suggestions[:20]  # Return top 20 suggestions

def main():
    print("AI-Agent User Database Check")
    print("=" * 50)
    
    # Check existing users
    existing_users = check_existing_users()
    
    # Suggest available usernames
    if existing_users:
        print(f"\nSuggested available usernames:")
        print("-" * 40)
        suggestions = suggest_usernames(existing_users)
        
        if suggestions:
            for i, username in enumerate(suggestions[:10], 1):
                print(f"{i:2d}. {username}")
        else:
            print("All common usernames are taken. Try custom variations.")
    else:
        print("\nDatabase is empty. Any username is available!")
        print("Suggested starter usernames:")
        starter_names = ["admin", "demo", "test", "user1", "manager"]
        for i, name in enumerate(starter_names, 1):
            print(f"{i:2d}. {name}")
    
    # Show demo credentials
    print(f"\nDemo Credentials (if demo user exists):")
    print("Username: demo")
    print("Password: demo1234")
    
    print(f"\nTo create a new user, use:")
    print("curl -X POST http://localhost:9000/users/register \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"username": "newuser", "email": "user@example.com", "password": "password123"}\'')

if __name__ == "__main__":
    main()