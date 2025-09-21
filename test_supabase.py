#!/usr/bin/env python3
"""
Test Supabase connection and create tables
"""

import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def test_supabase_connection():
    """Test connection to Supabase"""
    try:
        from core.database import DatabaseManager, create_db_and_tables, engine
        from core.models import User, Content, Feedback, Script
        from sqlmodel import Session, select
        
        print("Testing Supabase connection...")
        
        # Test basic connection
        with Session(engine) as session:
            result = session.exec(select(1)).first()
            print(f"[OK] Database connection successful: {result}")
        
        # Create tables
        print("Creating tables...")
        create_db_and_tables()
        print("[OK] Tables created/verified")
        
        # Test DatabaseManager
        db = DatabaseManager()
        analytics = db.get_analytics_data()
        print(f"[OK] Analytics query successful: {analytics}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Supabase connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_operations():
    """Test basic CRUD operations"""
    try:
        from core.database import DatabaseManager
        import uuid
        
        print("\nTesting data operations...")
        db = DatabaseManager()
        
        # Test user creation
        test_user_data = {
            'user_id': f'test_{uuid.uuid4().hex[:8]}',
            'username': f'testuser_{int(time.time())}',
            'password_hash': 'test_hash',
            'email': 'test@example.com',
            'created_at': time.time()
        }
        
        user = db.create_user(test_user_data)
        print(f"[OK] User created: {user.user_id}")
        
        # Test content creation
        test_content_data = {
            'content_id': f'content_{uuid.uuid4().hex[:8]}',
            'uploader_id': user.user_id,
            'title': 'Test Content',
            'description': 'Test Description',
            'file_path': '/test/path.mp4',
            'content_type': 'video/mp4',
            'authenticity_score': 0.8,
            'current_tags': '["test", "video"]',
            'uploaded_at': time.time()
        }
        
        content = db.create_content(test_content_data)
        print(f"[OK] Content created: {content.content_id}")
        
        # Test script creation
        test_script_data = {
            'script_id': f'script_{uuid.uuid4().hex[:8]}',
            'content_id': content.content_id,
            'user_id': user.user_id,
            'title': 'Test Script',
            'script_content': 'This is a test script content.',
            'script_type': 'text',
            'file_path': '/test/script.txt',
            'used_for_generation': True
        }
        
        script = db.create_script(test_script_data)
        if script:
            print(f"[OK] Script created: {script.script_id}")
        else:
            print("[WARN] Script creation failed (table may not exist)")
        
        # Test feedback creation
        test_feedback_data = {
            'content_id': content.content_id,
            'user_id': user.user_id,
            'event_type': 'like',
            'rating': 5,
            'comment': 'Great content!',
            'reward': 1.0,
            'timestamp': time.time()
        }
        
        feedback = db.create_feedback(test_feedback_data)
        print(f"[OK] Feedback created: {feedback.id}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Data operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=== Supabase Connection Test ===")
    
    # Check environment
    db_url = os.getenv('DATABASE_URL', 'Not set')
    print(f"Database URL: {db_url[:50]}...")
    
    if 'sqlite' in db_url.lower():
        print("[WARN] Still using SQLite, not Supabase!")
        return False
    
    connection_ok = test_supabase_connection()
    if not connection_ok:
        return False
    
    data_ok = test_data_operations()
    
    if connection_ok and data_ok:
        print("\n[SUCCESS] Supabase is working correctly!")
        print("Your data will now be saved to Supabase database.")
        return True
    else:
        print("\n[FAIL] Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)