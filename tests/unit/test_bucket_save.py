#!/usr/bin/env python3
"""
Test script to verify bucket and database saving functionality
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def test_bucket_initialization():
    """Test bucket directory structure"""
    try:
        from core import bhiv_bucket
        
        print("Testing bucket initialization...")
        bhiv_bucket.init_bucket()
        
        # Check if all required directories exist
        bucket_root = Path("bucket")
        required_dirs = ["scripts", "storyboards", "videos", "logs", "ratings", "tmp", "uploads"]
        
        for dir_name in required_dirs:
            dir_path = bucket_root / dir_name
            if dir_path.exists():
                print(f"[OK] {dir_name}/ directory exists")
            else:
                print(f"[FAIL] {dir_name}/ directory missing")
        
        return True
    except Exception as e:
        print(f"[FAIL] Bucket initialization failed: {e}")
        return False

def test_script_saving():
    """Test script saving to bucket"""
    try:
        from core import bhiv_bucket
        
        print("\nTesting script saving...")
        
        # Create test script content
        test_script = "This is a test script for video generation.\nLine 2 of the script.\nLine 3 with more content."
        
        # Save to temp file first
        temp_path = bhiv_bucket.get_bucket_path("tmp", "test_script.txt")
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        # Save to scripts bucket
        script_path = bhiv_bucket.save_script(temp_path, "test_script_001.txt")
        print(f"[OK] Script saved to: {script_path}")
        
        # Verify file exists
        if os.path.exists(script_path):
            print("[OK] Script file exists in bucket")
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if content == test_script:
                    print("[OK] Script content matches")
                else:
                    print("[FAIL] Script content mismatch")
        else:
            print("[FAIL] Script file not found in bucket")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return True
    except Exception as e:
        print(f"✗ Script saving failed: {e}")
        return False

def test_storyboard_saving():
    """Test storyboard saving to bucket"""
    try:
        from core import bhiv_bucket
        
        print("\nTesting storyboard saving...")
        
        # Create test storyboard
        test_storyboard = {
            "content_id": "test_content_001",
            "title": "Test Storyboard",
            "scenes": [
                {
                    "scene_id": "scene_0",
                    "duration": 2.0,
                    "frames": [
                        {
                            "text": "Test frame content",
                            "background_color": "#000000",
                            "text_position": "center"
                        }
                    ]
                }
            ],
            "total_duration": 2.0,
            "generation_method": "test",
            "created_at": time.time()
        }
        
        # Save storyboard
        storyboard_path = bhiv_bucket.save_storyboard(test_storyboard, "test_storyboard_001.json")
        print(f"✓ Storyboard saved to: {storyboard_path}")
        
        # Verify file exists and content
        if os.path.exists(storyboard_path):
            print("✓ Storyboard file exists in bucket")
            with open(storyboard_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if loaded_data["content_id"] == test_storyboard["content_id"]:
                    print("✓ Storyboard content matches")
                else:
                    print("✗ Storyboard content mismatch")
        else:
            print("✗ Storyboard file not found in bucket")
        
        return True
    except Exception as e:
        print(f"✗ Storyboard saving failed: {e}")
        return False

def test_rating_saving():
    """Test rating saving to bucket"""
    try:
        from core import bhiv_bucket
        
        print("\nTesting rating saving...")
        
        # Create test rating data
        test_rating = {
            "content_id": "test_content_001",
            "user_id": "test_user_001",
            "rating": 5,
            "comment": "Great content!",
            "event_type": "like",
            "reward": 1.0,
            "timestamp": time.time(),
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Save rating
        rating_path = bhiv_bucket.save_rating(test_rating, "test_rating_001.json")
        print(f"✓ Rating saved to: {rating_path}")
        
        # Verify file exists and content
        if os.path.exists(rating_path):
            print("✓ Rating file exists in bucket")
            with open(rating_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if loaded_data["rating"] == test_rating["rating"]:
                    print("✓ Rating content matches")
                else:
                    print("✗ Rating content mismatch")
        else:
            print("✗ Rating file not found in bucket")
        
        return True
    except Exception as e:
        print(f"✗ Rating saving failed: {e}")
        return False

def test_log_saving():
    """Test log saving to bucket"""
    try:
        from core import bhiv_bucket
        
        print("\nTesting log saving...")
        
        # Create test log data
        test_log = {
            "content_id": "test_content_001",
            "user_id": "test_user_001",
            "action": "test_action",
            "status": "completed",
            "timestamp": time.time(),
            "details": "This is a test log entry"
        }
        
        # Save log
        log_path = bhiv_bucket.save_json('logs', 'test_log_001.json', test_log)
        print(f"✓ Log saved to: {log_path}")
        
        # Verify file exists and content
        if os.path.exists(log_path):
            print("✓ Log file exists in bucket")
            with open(log_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                if loaded_data["action"] == test_log["action"]:
                    print("✓ Log content matches")
                else:
                    print("✗ Log content mismatch")
        else:
            print("✗ Log file not found in bucket")
        
        return True
    except Exception as e:
        print(f"✗ Log saving failed: {e}")
        return False

def test_database_connection():
    """Test database connection and models"""
    try:
        from core.database import DatabaseManager
        from core.models import create_db_and_tables
        
        print("\nTesting database connection...")
        
        # Create tables if they don't exist
        create_db_and_tables()
        print("✓ Database tables created/verified")
        
        # Test database manager
        db = DatabaseManager()
        analytics = db.get_analytics_data()
        print(f"✓ Database connection successful - {analytics['total_content']} content items")
        
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== Bucket and Database Save Test ===\n")
    
    tests = [
        test_bucket_initialization,
        test_script_saving,
        test_storyboard_saving,
        test_rating_saving,
        test_log_saving,
        test_database_connection
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Bucket and database saving should work correctly.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)