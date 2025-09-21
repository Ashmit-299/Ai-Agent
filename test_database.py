#!/usr/bin/env python3
"""
Test database functionality and create sample data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from core.database import DatabaseManager
from core.models import create_db_and_tables
import uuid
import time
import json

def test_database():
    print("Testing database functionality...")
    
    # Create tables
    try:
        create_db_and_tables()
        print("[PASS] Database tables created/verified")
    except Exception as e:
        print(f"[FAIL] Table creation failed: {e}")
        return False
    
    # Test database manager
    try:
        db = DatabaseManager()
        
        # Get analytics to see current state
        analytics = db.get_analytics_data()
        print(f"Current database state:")
        print(f"   Users: {analytics['total_users']}")
        print(f"   Content: {analytics['total_content']}")
        print(f"   Feedback: {analytics['total_feedback']}")
        print(f"   Scripts: {analytics['total_scripts']}")
        
        # Create test content if none exists
        if analytics['total_content'] == 0:
            print("Creating test content...")
            
            test_content_data = {
                'content_id': f'test_{uuid.uuid4().hex[:8]}',
                'uploader_id': 'demo001',
                'title': 'Test Content',
                'description': 'Sample content for testing',
                'file_path': 'test_file.txt',
                'content_type': 'text/plain',
                'duration_ms': 5000,
                'authenticity_score': 0.8,
                'current_tags': json.dumps(['test', 'sample']),
                'uploaded_at': time.time()
            }
            
            content = db.create_content(test_content_data)
            print(f"[PASS] Created test content: {content.content_id}")
            
            # Create test script
            test_script_data = {
                'script_id': f'script_{uuid.uuid4().hex[:8]}',
                'content_id': content.content_id,
                'user_id': 'demo001',
                'title': 'Test Script',
                'script_content': 'This is a test script\nWith multiple lines\nFor testing purposes',
                'script_type': 'text',
                'used_for_generation': True
            }
            
            script = db.create_script(test_script_data)
            if script:
                print(f"[PASS] Created test script: {script.script_id}")
            else:
                print("[WARN] Script table not available, skipping script creation")
            
            # Create test feedback
            test_feedback_data = {
                'content_id': content.content_id,
                'user_id': 'demo001',
                'event_type': 'like',
                'rating': 4,
                'comment': 'Great test content!',
                'reward': 0.5,
                'timestamp': time.time()
            }
            
            feedback = db.create_feedback(test_feedback_data)
            if feedback:
                print(f"[PASS] Created test feedback: {feedback.id}")
            else:
                print("[WARN] Feedback creation failed")
            
            return content.content_id
        else:
            # Get first content ID for testing
            from sqlmodel import Session, select
            from core.models import Content
            
            with Session(db.engine) as session:
                content = session.exec(select(Content)).first()
                return content.content_id if content else None
                
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    content_id = test_database()
    if content_id:
        print(f"\nDatabase test completed successfully!")
        print(f"Test content ID: {content_id}")
        print(f"Test metadata endpoint: http://localhost:9000/content/{content_id}/metadata")
    else:
        print("\nDatabase test failed")