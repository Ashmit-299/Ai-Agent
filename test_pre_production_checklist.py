#!/usr/bin/env python3
"""
Test Pre-Production Checklist Implementation
Validates that the pre-production checklist works correctly
"""

import os
import sys
import subprocess
import time
import requests
import json

def test_checklist_script_exists():
    """Test that the pre-production checklist script exists"""
    script_path = "scripts/pre_production_checklist.py"
    if os.path.exists(script_path):
        print("PASS: Pre-production checklist script exists")
        return True
    else:
        print("FAIL: Pre-production checklist script missing")
        return False

def test_deployment_validation_script_exists():
    """Test that the deployment validation script exists"""
    script_path = "scripts/deployment/deployment_validation.py"
    if os.path.exists(script_path):
        print("PASS: Deployment validation script exists")
        return True
    else:
        print("FAIL: Deployment validation script missing")
        return False

def test_documentation_exists():
    """Test that the deployment guide exists"""
    doc_path = "docs/PRE_PRODUCTION_DEPLOYMENT_GUIDE.md"
    if os.path.exists(doc_path):
        print("PASS: Pre-production deployment guide exists")
        return True
    else:
        print("FAIL: Pre-production deployment guide missing")
        return False

def test_server_is_running():
    """Test if the server is running on port 9000"""
    try:
        response = requests.get("http://localhost:9000/health", timeout=5)
        if response.status_code == 200:
            print("PASS: Server is running on port 9000")
            return True
        else:
            print(f"FAIL: Server responded with status {response.status_code}")
            return False
    except Exception as e:
        print(f"FAIL: Server not accessible: {e}")
        return False

def test_checklist_execution():
    """Test executing the pre-production checklist"""
    try:
        print("\nTesting pre-production checklist execution...")
        
        # Run the checklist script
        result = subprocess.run([
            sys.executable, 
            "scripts/pre_production_checklist_100_percent.py",
            "--api-url", "http://localhost:9000"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("PASS: Pre-production checklist executed successfully")
            
            # Check if report was generated
            if os.path.exists("production-readiness-report.json"):
                print("PASS: Production readiness report generated")
                
                # Load and validate report structure
                with open("production-readiness-report.json", "r") as f:
                    report = json.load(f)
                
                required_fields = ["timestamp", "overall_status", "total_checks", "passed_checks"]
                if all(field in report for field in required_fields):
                    print("PASS: Report structure is valid")
                    print(f"  - Status: {report['overall_status']}")
                    print(f"  - Checks: {report['passed_checks']}/{report['total_checks']}")
                    return True
                else:
                    print("FAIL: Report structure is invalid")
                    return False
            else:
                print("FAIL: Production readiness report not generated")
                return False
        else:
            print(f"FAIL: Pre-production checklist failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FAIL: Pre-production checklist timed out")
        return False
    except Exception as e:
        print(f"FAIL: Error running pre-production checklist: {e}")
        return False

def test_deployment_validation_execution():
    """Test executing the deployment validation script"""
    try:
        print("\nTesting deployment validation execution...")
        
        # Run the deployment validation script
        result = subprocess.run([
            sys.executable, 
            "scripts/deployment/deployment_validation_100_percent.py",
            "--api-url", "http://localhost:9000",
            "--timeout", "60"
        ], capture_output=True, text=True, timeout=90)
        
        if result.returncode == 0:
            print("PASS: Deployment validation executed successfully")
            
            # Check if report was generated
            if os.path.exists("deployment-validation-report.json"):
                print("PASS: Deployment validation report generated")
                
                # Load and validate report structure
                with open("deployment-validation-report.json", "r") as f:
                    report = json.load(f)
                
                required_fields = ["timestamp", "deployment_status", "total_tests", "passed_tests"]
                if all(field in report for field in required_fields):
                    print("PASS: Validation report structure is valid")
                    print(f"  - Status: {report['deployment_status']}")
                    print(f"  - Tests: {report['passed_tests']}/{report['total_tests']}")
                    return True
                else:
                    print("FAIL: Validation report structure is invalid")
                    return False
            else:
                print("FAIL: Deployment validation report not generated")
                return False
        else:
            print(f"FAIL: Deployment validation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("FAIL: Deployment validation timed out")
        return False
    except Exception as e:
        print(f"FAIL: Error running deployment validation: {e}")
        return False

def test_ci_cd_integration():
    """Test CI/CD pipeline integration"""
    ci_cd_path = ".github/workflows/ci-cd-production.yml"
    if os.path.exists(ci_cd_path):
        with open(ci_cd_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check for pre-production check integration
        if "pre-production-check:" in content and "pre_production_checklist.py" in content:
            print("PASS: CI/CD pipeline includes pre-production checks")
            
            # Check for deployment validation integration
            if "deployment_validation.py" in content:
                print("PASS: CI/CD pipeline includes deployment validation")
                return True
            else:
                print("FAIL: CI/CD pipeline missing deployment validation")
                return False
        else:
            print("FAIL: CI/CD pipeline missing pre-production checks")
            return False
    else:
        print("FAIL: CI/CD pipeline file not found")
        return False

def cleanup_test_files():
    """Clean up generated test files"""
    test_files = [
        "production-readiness-report.json",
        "deployment-validation-report.json"
    ]
    
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Cleaned up {file}")

def main():
    """Main test function"""
    print("Testing Pre-Production Checklist Implementation")
    print("=" * 60)
    
    tests = [
        ("Script Files", test_checklist_script_exists),
        ("Validation Script", test_deployment_validation_script_exists),
        ("Documentation", test_documentation_exists),
        ("Server Status", test_server_is_running),
        ("Checklist Execution", test_checklist_execution),
        ("Validation Execution", test_deployment_validation_execution),
        ("CI/CD Integration", test_ci_cd_integration)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            if test_func():
                passed_tests += 1
            else:
                print(f"   FAIL: {test_name} test failed")
        except Exception as e:
            print(f"   ERROR: {test_name} test error: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if passed_tests == total_tests:
        print("\nALL TESTS PASSED!")
        print("   Pre-production checklist implementation is working correctly")
        print("   System is ready for deployment validation")
    else:
        print(f"\n{total_tests - passed_tests} TESTS FAILED")
        print("   Review failed tests above")
        print("   Fix issues before proceeding with deployment")
    
    # Cleanup
    cleanup_test_files()
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)