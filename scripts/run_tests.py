#!/usr/bin/env python3
"""
Simple test runner for the project
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

load_dotenv()

def run_unit_tests():
    """Run unit tests"""
    print("=== Running Unit Tests ===")
    
    # Test bucket functionality
    try:
        from tests.unit.test_bhiv_bucket import test_get_bucket_path
        from ..core.bhiv_bucket import get_bucket_path
        
        # Simple bucket test
        path = get_bucket_path("scripts", "test.txt")
        assert "scripts" in path
        print("[OK] Bucket path test passed")
    except Exception as e:
        print(f"[ERROR] Bucket test failed: {e}")
    
    # Test video generator
    try:
        from ..video.generator import create_simple_video
        import tempfile
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = os.path.join(tmp_dir, "test.mp4")
            result = create_simple_video("Test content", output_path, duration=1.0)
            assert os.path.exists(result)
            print("[OK] Video generator test passed")
    except Exception as e:
        print(f"[ERROR] Video generator test failed: {e}")
    
    # Test LM client fallback
    try:
        from ..core.bhiv_lm_client import get_llm_config
        config = get_llm_config()
        assert isinstance(config, dict)
        print("[OK] LM client test passed")
    except Exception as e:
        print(f"[ERROR] LM client test failed: {e}")

def run_integration_tests():
    """Run integration tests"""
    print("\n=== Running Integration Tests ===")
    
    # Test database connection
    try:
        from ..core.database import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        print("[OK] Database connection test passed")
    except Exception as e:
        print(f"[ERROR] Database test failed: {e}")
    
    # Test authentication configuration
    try:
        from ..app.auth import PUB_KEY, ALG
        assert PUB_KEY is not None
        assert ALG == "RS256"
        print("[OK] Authentication config test passed")
    except Exception as e:
        print(f"[ERROR] Auth config test failed: {e}")

def main():
    """Main test runner"""
    print("AI Content Uploader - Test Suite")
    print("=" * 40)
    
    run_unit_tests()
    run_integration_tests()
    
    print("\n=== Test Summary ===")
    print("Tests completed. Check output above for any failures.")
    print("For full API testing, start the server and run integration tests.")

if __name__ == "__main__":
    main()