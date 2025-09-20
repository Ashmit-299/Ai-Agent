#!/usr/bin/env python3
"""
Comprehensive test runner for BHIV system
Runs unit tests for bucket, core, and LM client modules
"""

import pytest
import sys
import os
from pathlib import Path

def run_all_tests():
    """Run all unit tests with coverage and detailed output"""
    
    # Add project root to Python path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    # Test configuration
    test_args = [
        "tests/",  # Test directory
        "-v",      # Verbose output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker checking
        "-x",      # Stop on first failure
        "--durations=10",  # Show 10 slowest tests
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        test_args.extend([
            "--cov=core",
            "--cov=app",
            "--cov=video",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        print("Running tests with coverage...")
    except ImportError:
        print("Running tests without coverage (install pytest-cov for coverage reports)...")
    
    # Run tests
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code

def run_specific_module(module_name):
    """Run tests for a specific module"""
    
    module_map = {
        "bucket": "tests/test_bhiv_bucket.py",
        "core": "tests/test_bhiv_core.py", 
        "lm": "tests/test_bhiv_lm_client.py",
        "lm_client": "tests/test_bhiv_lm_client.py",
        "components": "tests/test_bhiv_components.py",
        "auth": "tests/test_auth_security.py",
        "video": "tests/test_video_storyboard.py",
        "database": "tests/test_database_models.py"
    }
    
    if module_name not in module_map:
        print(f"Unknown module: {module_name}")
        print(f"Available modules: {', '.join(module_map.keys())}")
        return 1
    
    test_file = module_map[module_name]
    
    if not os.path.exists(test_file):
        print(f"Test file not found: {test_file}")
        return 1
    
    print(f"Running tests for {module_name} module...")
    
    test_args = [test_file, "-v", "--tb=short"]
    exit_code = pytest.main(test_args)
    
    return exit_code

def run_integration_tests():
    """Run integration tests that require real components"""
    
    print("Running integration tests...")
    
    test_args = [
        "tests/",
        "-v",
        "-k", "integration or end_to_end",
        "--tb=short"
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

def run_smoke_tests():
    """Run quick smoke tests to verify basic functionality"""
    
    print("Running smoke tests...")
    
    test_args = [
        "tests/",
        "-v", 
        "-k", "test_init or test_config or test_health",
        "--tb=line"
    ]
    
    exit_code = pytest.main(test_args)
    return exit_code

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="BHIV Test Runner")
    parser.add_argument(
        "command", 
        nargs="?", 
        default="all",
        choices=["all", "bucket", "core", "lm", "lm_client", "components", "auth", "video", "database", "integration", "smoke"],
        help="Test command to run"
    )
    
    args = parser.parse_args()
    
    if args.command == "all":
        exit_code = run_all_tests()
    elif args.command in ["bucket", "core", "lm", "lm_client", "components", "auth", "video", "database"]:
        exit_code = run_specific_module(args.command)
    elif args.command == "integration":
        exit_code = run_integration_tests()
    elif args.command == "smoke":
        exit_code = run_smoke_tests()
    else:
        print(f"Unknown command: {args.command}")
        exit_code = 1
    
    sys.exit(exit_code)