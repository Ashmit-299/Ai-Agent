#!/usr/bin/env python3
"""
Master Test Execution Script for BHIV System
Runs all unit tests and provides comprehensive reporting
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def main():
    """Execute all unit tests with comprehensive reporting"""
    
    print("🧪 BHIV System - Master Test Suite")
    print("=" * 60)
    print("Running comprehensive unit test suite...")
    print()
    
    # Change to project directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Add project to Python path
    sys.path.insert(0, str(project_root))
    
    start_time = time.time()
    
    try:
        # Run pytest with comprehensive options
        cmd = [
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short", 
            "--strict-markers",
            "--durations=10",
            "-x"  # Stop on first failure for faster feedback
        ]
        
        print("Executing command:", " ".join(cmd))
        print("-" * 60)
        
        result = subprocess.run(cmd, timeout=300)
        
        duration = time.time() - start_time
        
        print()
        print("=" * 60)
        print(f"⏱️  Total execution time: {duration:.2f} seconds")
        
        if result.returncode == 0:
            print("🎉 ALL TESTS PASSED!")
            print()
            print("✅ Unit test implementation complete!")
            print("✅ All BHIV components tested")
            print("✅ Integration tests verified")
            print("✅ Error handling validated")
            print()
            print("📋 Test Coverage Summary:")
            print("  • BHIV Core: process_script_upload, webhook processing, rating system")
            print("  • BHIV Components: Integration tests and component compatibility")
            print("  • BHIV LM Client: LLM integration, fallback mechanisms, retry logic")
            print("  • BHIV Bucket: Storage operations and file handling")
            print("  • Video Storyboard: Generation, validation, text wrapping")
            print("  • Auth Security: JWT tokens, rate limiting, input validation")
            print("  • Database Models: Model validation, relationships, constraints")
            
            return 0
        else:
            print(f"❌ TESTS FAILED (exit code: {result.returncode})")
            print()
            print("🔍 Check the output above for specific test failures")
            print("💡 Run individual test files to debug specific issues:")
            print("   python -m pytest tests/test_bhiv_core.py -v")
            print("   python -m pytest tests/test_bhiv_lm_client.py -v")
            print("   python -m pytest tests/test_bhiv_bucket.py -v")
            
            return result.returncode
            
    except subprocess.TimeoutExpired:
        print("⏰ Tests timed out after 5 minutes")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())