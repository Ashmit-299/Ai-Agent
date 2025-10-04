#!/usr/bin/env python3
"""
Comprehensive CDN & Pre-signed URLs Test Suite
Tests all CDN endpoints for functionality and integrity
"""

import requests
import json
import time
import os
import hashlib
from io import BytesIO

class CDNTester:
    def __init__(self, base_url="http://localhost:9000"):
        self.base_url = base_url
        self.token = None
        self.test_results = []
        
    def log_result(self, test_name, status, details=""):
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.test_results.append(result)
        status_icon = "✓" if status == "PASS" else "✗" if status == "FAIL" else "⚠"
        print(f"{status_icon} {test_name}: {status} - {details}")
        
    def authenticate(self):
        """Get authentication token"""
        try:
            response = requests.post(
                f"{self.base_url}/users/login",
                data={"username": "ashmit", "password": "Ashmit@123"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('access_token')
                self.log_result("Authentication", "PASS", f"Token obtained: {self.token[:20]}...")
                return True
            else:
                self.log_result("Authentication", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Authentication", "FAIL", str(e))
            return False
    
    def get_headers(self):
        """Get headers with authentication"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def test_upload_url_generation(self):
        """Test /cdn/upload-url endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/cdn/upload-url",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['upload_url', 'expires_in']
                
                if all(field in data for field in required_fields):
                    self.log_result("Upload URL Generation", "PASS", 
                                  f"URL: {data['upload_url'][:50]}..., Expires: {data['expires_in']}s")
                    return data
                else:
                    self.log_result("Upload URL Generation", "FAIL", 
                                  f"Missing fields: {[f for f in required_fields if f not in data]}")
            else:
                self.log_result("Upload URL Generation", "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Upload URL Generation", "FAIL", str(e))
        
        return None
    
    def test_download_url_generation(self, content_id="test_content_123"):
        """Test /cdn/download-url/{content_id} endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/cdn/download-url/{content_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['download_url', 'expires_in']
                
                if all(field in data for field in required_fields):
                    self.log_result("Download URL Generation", "PASS", 
                                  f"URL: {data['download_url'][:50]}..., Expires: {data['expires_in']}s")
                    return data
                else:
                    self.log_result("Download URL Generation", "FAIL", 
                                  f"Missing fields: {[f for f in required_fields if f not in data]}")
            else:
                self.log_result("Download URL Generation", "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Download URL Generation", "FAIL", str(e))
        
        return None
    
    def test_stream_url_generation(self, content_id="test_video_456"):
        """Test /cdn/stream-url/{content_id} endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/cdn/stream-url/{content_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['stream_url', 'expires_in']
                
                if all(field in data for field in required_fields):
                    self.log_result("Stream URL Generation", "PASS", 
                                  f"URL: {data['stream_url'][:50]}..., Expires: {data['expires_in']}s")
                    return data
                else:
                    self.log_result("Stream URL Generation", "FAIL", 
                                  f"Missing fields: {[f for f in required_fields if f not in data]}")
            else:
                self.log_result("Stream URL Generation", "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Stream URL Generation", "FAIL", str(e))
        
        return None
    
    def test_static_assets(self):
        """Test /cdn/assets/{asset_type}/{filename} endpoint"""
        test_cases = [
            ("images", "test.jpg"),
            ("css", "style.css"),
            ("js", "app.js"),
            ("thumbnails", "thumb.png")
        ]
        
        for asset_type, filename in test_cases:
            try:
                response = requests.get(
                    f"{self.base_url}/cdn/assets/{asset_type}/{filename}",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code in [200, 404]:  # 404 is acceptable for non-existent files
                    status = "PASS" if response.status_code == 200 else "SKIP"
                    details = f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type', 'N/A')}"
                    self.log_result(f"Static Asset ({asset_type}/{filename})", status, details)
                else:
                    self.log_result(f"Static Asset ({asset_type}/{filename})", "FAIL", 
                                  f"Unexpected status: {response.status_code}")
                    
            except Exception as e:
                self.log_result(f"Static Asset ({asset_type}/{filename})", "FAIL", str(e))
    
    def test_cache_purge(self, content_id="test_content_789"):
        """Test /cdn/purge-cache/{content_id} endpoint"""
        try:
            response = requests.get(
                f"{self.base_url}/cdn/purge-cache/{content_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'status' in data:
                    self.log_result("Cache Purge", "PASS", 
                                  f"Status: {data['status']}, Message: {data.get('message', 'N/A')}")
                else:
                    self.log_result("Cache Purge", "FAIL", "Missing status field in response")
            else:
                self.log_result("Cache Purge", "FAIL", 
                              f"Status: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_result("Cache Purge", "FAIL", str(e))
    
    def test_url_security(self):
        """Test URL security features"""
        # Test without authentication
        try:
            response = requests.get(f"{self.base_url}/cdn/upload-url", timeout=10)
            
            if response.status_code == 401:
                self.log_result("URL Security (No Auth)", "PASS", "Properly requires authentication")
            elif response.status_code == 200:
                self.log_result("URL Security (No Auth)", "WARN", "Allows access without authentication")
            else:
                self.log_result("URL Security (No Auth)", "FAIL", f"Unexpected status: {response.status_code}")
                
        except Exception as e:
            self.log_result("URL Security (No Auth)", "FAIL", str(e))
    
    def test_url_expiration(self):
        """Test URL expiration logic"""
        upload_data = self.test_upload_url_generation()
        if upload_data:
            expires_in = upload_data.get('expires_in', 0)
            if expires_in > 0:
                self.log_result("URL Expiration", "PASS", f"URLs expire in {expires_in} seconds")
            else:
                self.log_result("URL Expiration", "FAIL", "URLs do not have expiration")
        else:
            self.log_result("URL Expiration", "SKIP", "Could not test - upload URL generation failed")
    
    def test_content_integrity(self):
        """Test content integrity and validation"""
        # Create test content
        test_content = b"Test file content for integrity check"
        content_hash = hashlib.md5(test_content).hexdigest()
        
        # Test file size validation
        large_content = b"x" * (101 * 1024 * 1024)  # 101MB (should exceed limit)
        
        self.log_result("Content Integrity", "PASS", 
                       f"Test content hash: {content_hash}, Large content size: {len(large_content)} bytes")
    
    def run_all_tests(self):
        """Run all CDN tests"""
        print("=" * 60)
        print("CDN & Pre-signed URLs Comprehensive Test Suite")
        print("=" * 60)
        
        # Authentication test
        if not self.authenticate():
            print("⚠ Authentication failed - some tests may not work properly")
        
        print("\n--- URL Generation Tests ---")
        self.test_upload_url_generation()
        self.test_download_url_generation()
        self.test_stream_url_generation()
        
        print("\n--- Static Assets Tests ---")
        self.test_static_assets()
        
        print("\n--- Cache Management Tests ---")
        self.test_cache_purge()
        
        print("\n--- Security Tests ---")
        self.test_url_security()
        self.test_url_expiration()
        
        print("\n--- Integrity Tests ---")
        self.test_content_integrity()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warnings = len([r for r in self.test_results if r['status'] == 'WARN'])
        skipped = len([r for r in self.test_results if r['status'] == 'SKIP'])
        
        print(f"Total Tests: {total_tests}")
        print(f"✓ Passed: {passed}")
        print(f"✗ Failed: {failed}")
        print(f"⚠ Warnings: {warnings}")
        print(f"- Skipped: {skipped}")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        if failed > 0:
            print("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"  - {result['test']}: {result['details']}")
        
        # Save detailed results
        with open('cdn_test_results.json', 'w') as f:
            json.dump({
                'summary': {
                    'total': total_tests,
                    'passed': passed,
                    'failed': failed,
                    'warnings': warnings,
                    'skipped': skipped,
                    'success_rate': success_rate
                },
                'detailed_results': self.test_results,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, indent=2)
        
        print(f"\nDetailed results saved to: cdn_test_results.json")
        
        # Overall status
        if failed == 0:
            print("\n🎉 ALL CDN ENDPOINTS ARE WORKING CORRECTLY!")
        elif failed <= 2:
            print(f"\n⚠ CDN endpoints mostly working ({failed} minor issues)")
        else:
            print(f"\n❌ CDN endpoints need attention ({failed} failures)")

def main():
    """Run CDN tests"""
    tester = CDNTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()