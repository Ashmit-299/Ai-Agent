#!/usr/bin/env python3
"""
Quick test script to verify the main fixes work
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        import core.bhiv_bucket
        import core.bhiv_lm_client
        import core.database
        import app.auth
        import video.storyboard
        print("[OK] All imports successful")
        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    try:
        from core.database import DatabaseManager
        db = DatabaseManager()
        print("[OK] Database manager created")
        return True
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False

def test_auth():
    """Test auth functionality"""
    try:
        from app.auth import hash_password, verify_password, create_access_token
        
        # Test password hashing
        password = "test123"
        hashed = hash_password(password)
        assert verify_password(password, hashed)
        
        # Test token creation
        token = create_access_token({"sub": "testuser", "user_id": "user123"})
        assert len(token) > 0
        
        print("[OK] Auth functions working")
        return True
    except Exception as e:
        print(f"[FAIL] Auth test failed: {e}")
        return False

def test_lm_client():
    """Test LM client functionality"""
    try:
        from core.bhiv_lm_client import is_llm_configured, get_llm_config
        
        configured = is_llm_configured()
        config = get_llm_config()
        
        print(f"[OK] LM client working (configured: {configured})")
        return True
    except Exception as e:
        print(f"[FAIL] LM client test failed: {e}")
        return False

def test_storyboard():
    """Test storyboard functionality"""
    try:
        from video.storyboard import generate_storyboard_from_text, wrap_text_for_storyboard
        
        # Test storyboard generation
        storyboard = generate_storyboard_from_text("Test script content")
        assert "scenes" in storyboard
        assert len(storyboard["scenes"]) > 0
        
        # Test text wrapping
        wrapped = wrap_text_for_storyboard("This is a very long text that should be wrapped properly")
        assert len(wrapped) > 0
        
        print("[OK] Storyboard functions working")
        return True
    except Exception as e:
        print(f"[FAIL] Storyboard test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running quick verification tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_database,
        test_auth,
        test_lm_client,
        test_storyboard
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: All core functionality working!")
        return 0
    else:
        print("WARNING: Some issues remain")
        return 1

if __name__ == "__main__":
    sys.exit(main())