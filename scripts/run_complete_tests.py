#!/usr/bin/env python3
"""
Complete Test Suite Runner
Runs all tests with coverage reporting and performance benchmarks
"""

import subprocess
import sys
import os
import json
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRunner:
    """Complete test suite runner with reporting"""
    
    def __init__(self):
        self.results = {
            "start_time": time.time(),
            "unit_tests": {"status": "pending", "coverage": 0},
            "integration_tests": {"status": "pending", "coverage": 0},
            "performance_tests": {"status": "pending", "benchmark": {}},
            "e2e_tests": {"status": "pending", "workflow": {}},
            "overall_coverage": 0,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
    
    def run_command(self, command: str, description: str) -> bool:
        """Run shell command and capture result"""
        logger.info(f"Running: {description}")
        logger.info(f"Command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"SUCCESS: {description}")
                return True
            else:
                logger.error(f"FAILED: {description}")
                logger.error(f"STDOUT: {result.stdout}")
                logger.error(f"STDERR: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"TIMEOUT: {description}")
            return False
        except Exception as e:
            logger.error(f"ERROR: {description} - {e}")
            return False
    
    def run_unit_tests(self) -> bool:
        """Run unit tests with coverage"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING UNIT TESTS")
        logger.info("="*60)
        
        success = self.run_command(
            "pytest tests/unit/ -v --cov=app --cov=core --cov=video --cov-report=xml --cov-report=html --junitxml=unit-test-results.xml",
            "Unit Tests with Coverage"
        )
        
        self.results["unit_tests"]["status"] = "passed" if success else "failed"
        
        # Extract coverage if available
        try:
            if os.path.exists("coverage.xml"):
                # Parse coverage from XML (simplified)
                with open("coverage.xml", "r") as f:
                    content = f.read()
                    if 'line-rate=' in content:
                        import re
                        match = re.search(r'line-rate="([\d.]+)"', content)
                        if match:
                            coverage = float(match.group(1)) * 100
                            self.results["unit_tests"]["coverage"] = round(coverage, 1)
        except Exception as e:
            logger.warning(f"Could not parse coverage: {e}")
        
        return success
    
    def run_integration_tests(self) -> bool:
        """Run integration tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING INTEGRATION TESTS")
        logger.info("="*60)
        
        success = self.run_command(
            "pytest tests/integration/ -v --junitxml=integration-test-results.xml",
            "Integration Tests"
        )
        
        self.results["integration_tests"]["status"] = "passed" if success else "failed"
        return success
    
    def run_performance_tests(self) -> bool:
        """Run performance benchmarks"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING PERFORMANCE TESTS")
        logger.info("="*60)
        
        success = self.run_command(
            "pytest tests/integration/test_performance_benchmarks.py -v -s --junitxml=performance-test-results.xml",
            "Performance Benchmarks"
        )
        
        self.results["performance_tests"]["status"] = "passed" if success else "failed"
        return success
    
    def run_e2e_tests(self) -> bool:
        """Run end-to-end workflow tests"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING END-TO-END TESTS")
        logger.info("="*60)
        
        success = self.run_command(
            "pytest tests/integration/test_complete_workflow.py -v -s --junitxml=e2e-test-results.xml",
            "End-to-End Workflow Tests"
        )
        
        self.results["e2e_tests"]["status"] = "passed" if success else "failed"
        return success
    
    def run_load_tests(self) -> bool:
        """Run load tests if available"""
        logger.info("\n" + "="*60)
        logger.info("RUNNING LOAD TESTS")
        logger.info("="*60)
        
        if os.path.exists("tests/load_testing"):
            success = self.run_command(
                "pytest tests/load_testing/ -v --junitxml=load-test-results.xml",
                "Load Tests"
            )
        else:
            logger.info("Load tests directory not found, skipping")
            success = True
        
        return success
    
    def generate_report(self):
        """Generate comprehensive test report"""
        end_time = time.time()
        duration = end_time - self.results["start_time"]
        
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE TEST REPORT")
        logger.info("="*80)
        
        logger.info(f"Total Test Duration: {duration:.1f} seconds")
        logger.info("")
        
        # Test Results Summary
        test_categories = ["unit_tests", "integration_tests", "performance_tests", "e2e_tests"]
        
        for category in test_categories:
            status = self.results[category]["status"]
            emoji = "PASS" if status == "passed" else "FAIL" if status == "failed" else "PEND"
            category_name = category.replace("_", " ").title()
            
            logger.info(f"{emoji} {category_name}: {status.upper()}")
            
            if category == "unit_tests" and self.results[category].get("coverage", 0) > 0:
                coverage = self.results[category]["coverage"]
                coverage_emoji = "GOOD" if coverage >= 70 else "LOW"
                logger.info(f"   {coverage_emoji} Coverage: {coverage}%")
        
        # Overall Status
        all_passed = all(
            self.results[cat]["status"] == "passed" 
            for cat in test_categories
        )
        
        logger.info("")
        if all_passed:
            logger.info("ALL TESTS PASSED - PRODUCTION READY!")
            logger.info("System is ready for deployment")
        else:
            logger.info("SOME TESTS FAILED - NEEDS ATTENTION")
            logger.info("Review failed tests before deployment")
        
        # Coverage Summary
        unit_coverage = self.results["unit_tests"].get("coverage", 0)
        if unit_coverage > 0:
            logger.info(f"\nTest Coverage: {unit_coverage}%")
            if unit_coverage >= 70:
                logger.info("Coverage meets requirement (>=70%)")
            else:
                logger.info(f"Coverage below requirement: {unit_coverage}% < 70%")
        
        # Save results to JSON
        self.results["end_time"] = end_time
        self.results["duration"] = duration
        self.results["overall_status"] = "passed" if all_passed else "failed"
        
        with open("test-report.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        logger.info(f"\nTest reports saved:")
        logger.info("  - test-report.json (machine readable)")
        logger.info("  - htmlcov/index.html (coverage report)")
        logger.info("  - *-test-results.xml (JUnit format)")
        
        return all_passed

def main():
    """Main test runner"""
    logger.info("Starting Comprehensive Test Suite")
    
    # Ensure we're in the right directory
    if not os.path.exists("app") or not os.path.exists("tests"):
        logger.error("Must run from project root directory")
        sys.exit(1)
    
    runner = TestRunner()
    
    # Run all test suites
    results = []
    results.append(runner.run_unit_tests())
    results.append(runner.run_integration_tests())
    results.append(runner.run_performance_tests())
    results.append(runner.run_e2e_tests())
    results.append(runner.run_load_tests())
    
    # Generate report
    overall_success = runner.generate_report()
    
    # Exit with appropriate code
    if overall_success:
        logger.info("Test suite completed successfully!")
        sys.exit(0)
    else:
        logger.error("Test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()