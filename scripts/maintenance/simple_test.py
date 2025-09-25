#!/usr/bin/env python3
"""
Simple test script to verify bucket and database saving functionality
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(__file__))

def test_bucket_functionality():
    """Test basic bucket functionality"""
    try:
        from core import bhiv_bucket
        
        print("Testing bucket functionality...")
        
        # Initialize bucket
        bhiv_bucket.init_bucket()
        print("[OK] Bucket initialized")
        
        # Test script saving
        test_script = "This is a test script.\nSecond line.\nThird line."
        temp_path = bhiv_bucket.get_bucket_path("tmp", "test.txt")
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        script_path = bhiv_bucket.save_script(temp_path, "test_script.txt")
        print(f"[OK] Script saved to: {script_path}")
        
        # Test storyboard saving
        storyboard_data = {
            "content_id": "test_001",
            "scenes": [{"text": "Test scene"}],
            "created_at": time.time()
        }
        
        storyboard_path = bhiv_bucket.save_storyboard(storyboard_data, "test_storyboard.json")
        print(f"[OK] Storyboard saved to: {storyboard_path}")
        
        # Test rating saving
        rating_data = {
            "content_id": "test_001",
            "user_id": "test_user",
            "rating": 5,
            "timestamp": time.time()
        }
        
        rating_path = bhiv_bucket.save_rating(rating_data, "test_rating.json")
        print(f"[OK] Rating saved to: {rating_path}")
        
        # Test log saving
        log_data = {
            "action": "test",
            "status": "completed",
            "timestamp": time.time()
        }
        
        log_path = bhiv_bucket.save_json('logs', 'test_log.json', log_data)
        print(f"[OK] Log saved to: {log_path}")
        
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Bucket test failed: {e}")
        return False

def test_database_functionality():
    """Test database functionality"""
    try:
        from ..core.database import DatabaseManager
        from ..core.models import create_db_and_tables
        
        print("Testing database functionality...")
        
        # Create tables
        create_db_and_tables()
        print("[OK] Database tables created/verified")
        
        # Test database manager
        db = DatabaseManager()
        analytics = db.get_analytics_data()
        print(f"[OK] Database connection successful - {analytics.get('total_content', 0)} content items")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False

def main():
    """Run tests"""
    print("=== Simple Bucket and Database Test ===")
    print()
    
    bucket_ok = test_bucket_functionality()
    print()
    database_ok = test_database_functionality()
    print()
    
    if bucket_ok and database_ok:
        print("[SUCCESS] All tests passed!")
        print("Your video generation should now properly save:")
        print("- Scripts to bucket/scripts/ and database")
        print("- Storyboards to bucket/storyboards/")
        print("- Ratings to bucket/ratings/")
        print("- Logs to bucket/logs/")
        return True
    else:
        print("[FAIL] Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)