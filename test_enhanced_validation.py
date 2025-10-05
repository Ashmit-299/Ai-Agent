#!/usr/bin/env python3
"""
Test Enhanced Input Validation System
Comprehensive testing of the new validation middleware and enhanced upload endpoint
"""

import requests
import json
import time
import os
import tempfile
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:9000"
TEST_USER = {"username": "demo", "password": "demo1234"}

class ValidationTester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        self.results = []
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def authenticate(self) -> bool:
        """Get authentication token"""
        try:
            response = self.session.post(
                f"{BASE_URL}/users/login",
                data=TEST_USER
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.token}"
                    })
                    self.log_result("Authentication", True, "Token obtained successfully")
                    return True
            
            self.log_result("Authentication", False, f"Status: {response.status_code}")
            return False
            
        except Exception as e:
            self.log_result("Authentication", False, str(e))
            return False
    
    def test_file_size_validation(self):
        """Test file size limits"""
        print("\n=== Testing File Size Validation ===")
        
        # Test 1: Normal size file (should pass)
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                content = "This is a test file with normal size content."
                f.write(content.encode())
                f.flush()
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("test.txt", test_file, "text/plain")},
                        data={"title": "Normal Size Test", "description": "Test file"}
                    )
                
                if response.status_code == 201:
                    self.log_result("Normal File Size", True, "File uploaded successfully")
                else:
                    self.log_result("Normal File Size", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Normal File Size", False, str(e))
        
        # Test 2: Large file (should fail)
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                # Create a file larger than 100MB
                large_content = "X" * (101 * 1024 * 1024)  # 101MB
                f.write(large_content.encode())
                f.flush()
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("large_test.txt", test_file, "text/plain")},
                        data={"title": "Large File Test", "description": "Should fail"}
                    )
                
                if response.status_code == 413:
                    self.log_result("Large File Rejection", True, "Large file properly rejected")
                else:
                    self.log_result("Large File Rejection", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Large File Rejection", False, str(e))
    
    def test_file_type_validation(self):
        """Test file type restrictions"""
        print("\n=== Testing File Type Validation ===")
        
        # Test 1: Allowed file type (should pass)
        try:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                # Create a minimal JPEG header
                jpeg_header = b'\\xff\\xd8\\xff\\xe0\\x00\\x10JFIF'
                f.write(jpeg_header + b'\\x00' * 100)
                f.flush()
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("test.jpg", test_file, "image/jpeg")},
                        data={"title": "Valid Image Test", "description": "Should pass"}
                    )
                
                if response.status_code == 201:
                    self.log_result("Valid File Type", True, "JPEG file accepted")
                else:
                    self.log_result("Valid File Type", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Valid File Type", False, str(e))
        
        # Test 2: Dangerous file type (should fail)
        try:
            with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
                f.write(b'MZ\\x90\\x00\\x03\\x00\\x00\\x00')  # PE header
                f.flush()
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("malware.exe", test_file, "application/octet-stream")},
                        data={"title": "Dangerous File", "description": "Should fail"}
                    )
                
                if response.status_code == 400:
                    self.log_result("Dangerous File Rejection", True, "Executable file properly rejected")
                else:
                    self.log_result("Dangerous File Rejection", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Dangerous File Rejection", False, str(e))
    
    def test_text_sanitization(self):
        """Test text input sanitization"""
        print("\n=== Testing Text Sanitization ===")
        
        # Test 1: XSS attempt (should be sanitized)
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b'Safe content')
                f.flush()
                
                malicious_title = "<script>alert('XSS')</script>Malicious Title"
                malicious_desc = "javascript:alert('XSS')"
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("test.txt", test_file, "text/plain")},
                        data={"title": malicious_title, "description": malicious_desc}
                    )
                
                if response.status_code == 400:
                    self.log_result("XSS Prevention", True, "Malicious input properly rejected")
                elif response.status_code == 201:
                    # Check if content was sanitized
                    data = response.json()
                    if "<script>" not in data.get("title", "") and "javascript:" not in str(data):
                        self.log_result("XSS Prevention", True, "Malicious input sanitized")
                    else:
                        self.log_result("XSS Prevention", False, "XSS content not sanitized")
                else:
                    self.log_result("XSS Prevention", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("XSS Prevention", False, str(e))
        
        # Test 2: SQL injection attempt (should be rejected)
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                f.write(b'Safe content')
                f.flush()
                
                sql_injection = "'; DROP TABLE users; --"
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("test.txt", test_file, "text/plain")},
                        data={"title": "Normal Title", "description": sql_injection}
                    )
                
                if response.status_code == 400:
                    self.log_result("SQL Injection Prevention", True, "SQL injection properly rejected")
                else:
                    self.log_result("SQL Injection Prevention", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("SQL Injection Prevention", False, str(e))
    
    def test_malware_detection(self):
        """Test basic malware signature detection"""
        print("\n=== Testing Malware Detection ===")
        
        # Test EICAR test signature
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                # EICAR test signature
                eicar = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'
                f.write(eicar)
                f.flush()
                
                with open(f.name, 'rb') as test_file:
                    response = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("eicar.txt", test_file, "text/plain")},
                        data={"title": "EICAR Test", "description": "Should be detected"}
                    )
                
                if response.status_code == 400:
                    self.log_result("Malware Detection", True, "EICAR signature detected and blocked")
                else:
                    self.log_result("Malware Detection", False, f"Status: {response.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Malware Detection", False, str(e))
    
    def test_request_size_limits(self):
        """Test request body size limits"""
        print("\n=== Testing Request Size Limits ===")
        
        try:
            # Test with very large request body
            large_data = {"title": "X" * (50 * 1024 * 1024)}  # 50MB title
            
            response = self.session.post(
                f"{BASE_URL}/upload-enhanced",
                data=large_data
            )
            
            if response.status_code == 413:
                self.log_result("Request Size Limit", True, "Large request properly rejected")
            else:
                self.log_result("Request Size Limit", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_result("Request Size Limit", False, str(e))
    
    def test_enhanced_vs_regular_upload(self):
        """Compare enhanced vs regular upload endpoints"""
        print("\n=== Testing Enhanced vs Regular Upload ===")
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
                content = "Test content for comparison"
                f.write(content.encode())
                f.flush()
                
                # Test regular upload
                with open(f.name, 'rb') as test_file:
                    response1 = self.session.post(
                        f"{BASE_URL}/upload",
                        files={"file": ("test.txt", test_file, "text/plain")},
                        data={"title": "Regular Upload Test", "description": "Regular endpoint"}
                    )
                
                # Test enhanced upload
                with open(f.name, 'rb') as test_file:
                    response2 = self.session.post(
                        f"{BASE_URL}/upload-enhanced",
                        files={"file": ("test.txt", test_file, "text/plain")},
                        data={"title": "Enhanced Upload Test", "description": "Enhanced endpoint"}
                    )
                
                regular_success = response1.status_code in [200, 201]
                enhanced_success = response2.status_code in [200, 201]
                
                if regular_success and enhanced_success:
                    # Compare response data
                    try:
                        data1 = response1.json()
                        data2 = response2.json()
                        
                        has_validation_info = "validation" in data2
                        has_security_features = "file_hash" in str(data2) or "authenticity_score" in data2
                        
                        if has_validation_info and has_security_features:
                            self.log_result("Enhanced Features", True, "Enhanced endpoint provides additional security info")
                        else:
                            self.log_result("Enhanced Features", False, "Enhanced endpoint missing security features")
                    except:
                        self.log_result("Enhanced Features", False, "Could not parse response data")
                else:
                    self.log_result("Enhanced Features", False, f"Regular: {response1.status_code}, Enhanced: {response2.status_code}")
                
                os.unlink(f.name)
                
        except Exception as e:
            self.log_result("Enhanced Features", False, str(e))
    
    def run_all_tests(self):
        """Run comprehensive validation tests"""
        print("🔒 Enhanced Input Validation System Test")
        print("=" * 50)
        
        # Authenticate first
        if not self.authenticate():
            print("❌ Authentication failed - cannot run tests")
            return
        
        # Run all test categories
        self.test_file_size_validation()
        self.test_file_type_validation()
        self.test_text_sanitization()
        self.test_malware_detection()
        self.test_request_size_limits()
        self.test_enhanced_vs_regular_upload()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save detailed results
        try:
            with open("validation_test_results.json", "w") as f:
                json.dump({
                    "summary": {
                        "total_tests": total_tests,
                        "passed": passed_tests,
                        "failed": failed_tests,
                        "success_rate": (passed_tests/total_tests)*100
                    },
                    "results": self.results,
                    "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, indent=2)
            print(f"\n📄 Detailed results saved to: validation_test_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    """Main test execution"""
    print("Starting Enhanced Input Validation Tests...")
    print("Make sure the server is running on http://localhost:9000")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Make sure it's running on port 9000")
        return
    
    # Run tests
    tester = ValidationTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()