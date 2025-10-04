#!/usr/bin/env python3
"""
Comprehensive Test Runner for BHIV System
Executes all unit tests and provides detailed reporting
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def run_test_suite():
    """Run complete test suite with detailed reporting"""
    
    print("🧪 BHIV System - Complete Unit Test Suite")
    print("=" * 60)
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    test_files = [
        ("BHIV Core Tests", "tests/test_bhiv_core.py"),
        ("BHIV Components Tests", "tests/test_bhiv_components.py"), 
        ("BHIV LM Client Tests", "tests/test_bhiv_lm_client.py"),
        ("BHIV Bucket Tests", "tests/test_bhiv_bucket.py"),
        ("Video Storyboard Tests", "tests/test_video_storyboard.py"),
        ("Auth Security Tests", "tests/test_auth_security.py"),
        ("Database Models Tests", "tests/test_database_models.py")
    ]
    
    results = {}
    total_start_time = time.time()
    
    for test_name, test_file in test_files:
        print(f"\n📋 Running {test_name}...")
        print("-" * 40)
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            results[test_name] = "MISSING"
            continue
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",
                "--tb=short",
                "--no-header"
            ], capture_output=True, text=True, timeout=120)
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                print(f"✅ {test_name} PASSED ({duration:.2f}s)")
                results[test_name] = "PASSED"
            else:
                print(f"❌ {test_name} FAILED ({duration:.2f}s)")
                results[test_name] = "FAILED"
                print("STDOUT:", result.stdout[-500:] if result.stdout else "None")
                print("STDERR:", result.stderr[-500:] if result.stderr else "None")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {test_name} TIMEOUT")
            results[test_name] = "TIMEOUT"
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            results[test_name] = "ERROR"
    
    total_duration = time.time() - total_start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for status in results.values() if status == "PASSED")
    failed = sum(1 for status in results.values() if status == "FAILED")
    errors = sum(1 for status in results.values() if status in ["TIMEOUT", "ERROR", "MISSING"])
    
    for test_name, status in results.items():
        status_icon = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "TIMEOUT": "⏰",
            "ERROR": "💥",
            "MISSING": "❓"
        }.get(status, "❓")
        
        print(f"{status_icon} {test_name}: {status}")
    
    print(f"\n📈 Results: {passed} passed, {failed} failed, {errors} errors")
    print(f"⏱️  Total time: {total_duration:.2f}s")
    
    if failed == 0 and errors == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {failed + errors} test suites had issues")
        return 1

def run_quick_smoke_test():
    """Run quick smoke test to verify basic functionality"""
    
    print("🚀 Quick Smoke Test")
    print("-" * 30)
    
    try:
        # Test imports
        print("Testing imports...")
        
        import core.bhiv_core
        import core.bhiv_bucket  
        import core.bhiv_lm_client
        import video.storyboard
        import app.auth
        import app.models
        
        print("✅ All imports successful")
        
        # Test basic functionality
        print("Testing basic functionality...")
        
        # Test storyboard generation
        from video.storyboard import generate_storyboard_from_text, validate_storyboard
        test_script = "This is a test script"
        storyboard = generate_storyboard_from_text(test_script)
        
        if validate_storyboard(storyboard):
            print("✅ Storyboard generation works")
        else:
            print("❌ Storyboard validation failed")
            return 1
        
        # Test auth functions
        from app.auth import hash_password, verify_password
        test_password = "test123"
        hashed = hash_password(test_password)
        
        if verify_password(test_password, hashed):
            print("✅ Authentication functions work")
        else:
            print("❌ Authentication verification failed")
            return 1
        
        print("\n🎉 Smoke test passed!")
        return 0
        
    except Exception as e:
        print(f"❌ Smoke test failed: {e}")
        return 1

def main():
    """Main test runner entry point"""
    
    if len(sys.argv) > 1 and sys.argv[1] == "smoke":
        return run_quick_smoke_test()
    else:
        return run_test_suite()

if __name__ == "__main__":
    exit(main())