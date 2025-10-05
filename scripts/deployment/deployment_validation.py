#!/usr/bin/env python3
"""
Deployment Validation Script
Validates deployment success and system health post-deployment
"""

import os
import sys
import requests
import json
import time
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DeploymentValidator:
    """Validate deployment success and system health"""
    
    def __init__(self, api_base_url: str, timeout: int = 300):
        self.api_base_url = api_base_url
        self.timeout = timeout
        self.validation_results = []
        self.deployment_healthy = True
    
    def add_validation_result(self, test_name: str, status: bool, details: str = "", response_time: float = 0):
        """Add a validation result"""
        self.validation_results.append({
            "test_name": test_name,
            "status": "PASS" if status else "FAIL",
            "passed": status,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": time.time()
        })
        
        if not status:
            self.deployment_healthy = False
        
        logger.info(f"{'PASS' if status else 'FAIL'} {test_name} ({response_time*1000:.1f}ms)")
        if details:
            logger.info(f"    {details}")
    
    def wait_for_deployment(self):
        """Wait for deployment to be ready"""
        logger.info("Waiting for deployment to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.timeout:
            try:
                start_request = time.time()
                response = requests.get(f"{self.api_base_url}/health", timeout=10)
                response_time = time.time() - start_request
                
                if response.status_code == 200:
                    self.add_validation_result(
                        "Deployment Ready",
                        True,
                        f"Service responding after {time.time() - start_time:.1f}s",
                        response_time
                    )
                    return True
                    
            except Exception as e:
                logger.info(f"    Waiting... ({e})")
                time.sleep(10)
        
        self.add_validation_result(
            "Deployment Ready",
            False,
            f"Service not responding after {self.timeout}s timeout"
        )
        return False
    
    def validate_core_endpoints(self):
        """Validate core API endpoints"""
        logger.info("\nValidating Core Endpoints...")
        
        core_endpoints = [
            ("/health", "Health Check"),
            ("/health/detailed", "Detailed Health"),
            ("/docs", "API Documentation"),
            ("/openapi.json", "OpenAPI Schema"),
            ("/metrics", "Metrics Info")
        ]
        
        for endpoint, description in core_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=15)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.add_validation_result(
                        description,
                        True,
                        f"Status: {response.status_code}",
                        response_time
                    )
                else:
                    self.add_validation_result(
                        description,
                        False,
                        f"Status: {response.status_code}",
                        response_time
                    )
                    
            except Exception as e:
                self.add_validation_result(description, False, str(e))
    
    def validate_authentication_flow(self):
        """Validate authentication system"""
        logger.info("\nValidating Authentication Flow...")
        
        try:
            # Test demo login endpoint
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/demo-login", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                demo_data = response.json()
                self.add_validation_result(
                    "Demo Login Available",
                    True,
                    f"Username: {demo_data.get('username', 'N/A')}",
                    response_time
                )
                
                # Test actual login with demo credentials
                if 'username' in demo_data and 'password' in demo_data:
                    try:
                        login_data = {
                            "username": demo_data['username'],
                            "password": demo_data['password']
                        }
                        
                        start_time = time.time()
                        login_response = requests.post(
                            f"{self.api_base_url}/users/login",
                            data=login_data,
                            timeout=10
                        )
                        response_time = time.time() - start_time
                        
                        if login_response.status_code == 200:
                            token_data = login_response.json()
                            self.add_validation_result(
                                "Demo Login Flow",
                                True,
                                f"Token received: {token_data.get('token_type', 'unknown')}",
                                response_time
                            )
                        else:
                            self.add_validation_result(
                                "Demo Login Flow",
                                False,
                                f"Login failed: {login_response.status_code}",
                                response_time
                            )
                            
                    except Exception as e:
                        self.add_validation_result("Demo Login Flow", False, str(e))
            else:
                self.add_validation_result(
                    "Demo Login Available",
                    False,
                    f"Status: {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.add_validation_result("Authentication System", False, str(e))
    
    def validate_upload_system(self):
        """Validate file upload system"""
        logger.info("\nValidating Upload System...")
        
        try:
            # Test CDN upload URL generation
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/cdn/upload-url", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.add_validation_result(
                    "CDN Upload URL Generation",
                    True,
                    "Upload URL endpoint accessible",
                    response_time
                )
            else:
                self.add_validation_result(
                    "CDN Upload URL Generation",
                    False,
                    f"Status: {response.status_code}",
                    response_time
                )
            
            # Test content listing
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/contents", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                content_data = response.json()
                self.add_validation_result(
                    "Content Listing",
                    True,
                    f"Found {len(content_data.get('contents', []))} items",
                    response_time
                )
            else:
                self.add_validation_result(
                    "Content Listing",
                    False,
                    f"Status: {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.add_validation_result("Upload System", False, str(e))
    
    def validate_monitoring_system(self):
        """Validate monitoring and observability"""
        logger.info("\nValidating Monitoring System...")
        
        monitoring_endpoints = [
            ("/metrics/performance", "Performance Metrics"),
            ("/observability/health", "Observability Health"),
            ("/monitoring-status", "Monitoring Status")
        ]
        
        for endpoint, description in monitoring_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    self.add_validation_result(
                        description,
                        True,
                        "Monitoring endpoint accessible",
                        response_time
                    )
                else:
                    self.add_validation_result(
                        description,
                        False,
                        f"Status: {response.status_code}",
                        response_time
                    )
                    
            except Exception as e:
                self.add_validation_result(description, False, str(e))
    
    def validate_gdpr_compliance(self):
        """Validate GDPR compliance endpoints"""
        logger.info("\nValidating GDPR Compliance...")
        
        try:
            # Test privacy policy endpoint
            start_time = time.time()
            response = requests.get(f"{self.api_base_url}/gdpr/privacy-policy", timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.add_validation_result(
                    "GDPR Privacy Policy",
                    True,
                    "Privacy policy accessible",
                    response_time
                )
            else:
                self.add_validation_result(
                    "GDPR Privacy Policy",
                    False,
                    f"Status: {response.status_code}",
                    response_time
                )
                
        except Exception as e:
            self.add_validation_result("GDPR Compliance", False, str(e))
    
    def validate_performance_benchmarks(self):
        """Validate performance benchmarks"""
        logger.info("\nValidating Performance Benchmarks...")
        
        # Test response times for critical endpoints
        performance_tests = [
            ("/health", "Health Check", 2.0),  # Should respond within 2s
            ("/metrics", "Metrics", 3.0),      # Should respond within 3s
            ("/contents", "Content List", 5.0)  # Should respond within 5s
        ]
        
        for endpoint, description, max_time in performance_tests:
            try:
                start_time = time.time()
                response = requests.get(f"{self.api_base_url}{endpoint}", timeout=max_time + 1)
                response_time = time.time() - start_time
                
                if response.status_code == 200 and response_time <= max_time:
                    self.add_validation_result(
                        f"{description} Performance",
                        True,
                        f"Response time: {response_time:.2f}s (target: <{max_time}s)",
                        response_time
                    )
                elif response.status_code == 200:
                    self.add_validation_result(
                        f"{description} Performance",
                        False,
                        f"Too slow: {response_time:.2f}s (target: <{max_time}s)",
                        response_time
                    )
                else:
                    self.add_validation_result(
                        f"{description} Performance",
                        False,
                        f"Status: {response.status_code}",
                        response_time
                    )
                    
            except Exception as e:
                self.add_validation_result(f"{description} Performance", False, str(e))
    
    def run_full_validation(self) -> bool:
        """Run complete deployment validation"""
        logger.info("Starting Deployment Validation")
        logger.info("="*60)
        
        # Wait for deployment to be ready
        if not self.wait_for_deployment():
            return False
        
        # Run all validation tests
        self.validate_core_endpoints()
        self.validate_authentication_flow()
        self.validate_upload_system()
        self.validate_monitoring_system()
        self.validate_gdpr_compliance()
        self.validate_performance_benchmarks()
        
        return self.deployment_healthy
    
    def generate_validation_report(self):
        """Generate deployment validation report"""
        logger.info("\n" + "="*80)
        logger.info("DEPLOYMENT VALIDATION REPORT")
        logger.info("="*80)
        
        # Calculate statistics
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result["passed"])
        avg_response_time = sum(result["response_time_ms"] for result in self.validation_results) / total_tests if total_tests > 0 else 0
        
        # Print summary
        logger.info(f"\nSUMMARY")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {total_tests - passed_tests}")
        logger.info(f"   Success Rate: {(passed_tests/total_tests*100):.1f}%")
        logger.info(f"   Average Response Time: {avg_response_time:.1f}ms")
        
        # Print detailed results
        logger.info(f"\nDETAILED RESULTS")
        logger.info("-" * 60)
        
        for result in self.validation_results:
            status_text = "PASS" if result["passed"] else "FAIL"
            logger.info(f"{status_text} {result['test_name']} ({result['response_time_ms']}ms)")
            if result['details']:
                logger.info(f"    {result['details']}")
        
        # Overall status
        logger.info(f"\n" + "="*80)
        if self.deployment_healthy:
            logger.info("DEPLOYMENT VALIDATION SUCCESSFUL!")
            logger.info("   All critical systems are operational")
            logger.info("   Deployment is ready for production traffic")
        else:
            logger.info("DEPLOYMENT VALIDATION FAILED")
            logger.info("   Critical issues detected in deployment")
            logger.info("   Review failed tests above")
        
        logger.info("="*80)
        
        # Save detailed report
        report_data = {
            "timestamp": time.time(),
            "deployment_status": "HEALTHY" if self.deployment_healthy else "UNHEALTHY",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": (passed_tests/total_tests*100) if total_tests > 0 else 0,
            "average_response_time_ms": avg_response_time,
            "validation_results": self.validation_results,
            "api_base_url": self.api_base_url
        }
        
        with open("deployment-validation-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        logger.info("Detailed report saved to: deployment-validation-report.json")
        
        return self.deployment_healthy

def main():
    """Main validation function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deployment Validation")
    parser.add_argument("--api-url", required=True, help="API base URL to validate")
    parser.add_argument("--timeout", type=int, default=300, help="Timeout for deployment readiness (seconds)")
    args = parser.parse_args()
    
    validator = DeploymentValidator(args.api_url, args.timeout)
    
    try:
        validation_success = validator.run_full_validation()
        report_success = validator.generate_validation_report()
        
        if validation_success:
            logger.info("Deployment validation completed successfully!")
            sys.exit(0)
        else:
            logger.error("Deployment validation failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()