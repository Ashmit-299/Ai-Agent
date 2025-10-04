#!/usr/bin/env python3
"""
Comprehensive health check system for deployment verification
"""

import os
import sys
import time
import requests
import json
from typing import Dict, List, Any
from datetime import datetime

class HealthChecker:
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.results = []
    
    def check_endpoint(self, path: str, expected_status: int = 200, 
                      required_fields: List[str] = None) -> Dict[str, Any]:
        """Check a specific endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=self.timeout)
            duration = (time.time() - start_time) * 1000
            
            result = {
                "endpoint": path,
                "url": url,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "response_time_ms": round(duration, 2),
                "success": response.status_code == expected_status,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Check response content if JSON
            try:
                data = response.json()
                result["response_data"] = data
                
                # Check for required fields
                if required_fields:
                    missing_fields = [field for field in required_fields 
                                    if field not in data]
                    if missing_fields:
                        result["success"] = False
                        result["error"] = f"Missing required fields: {missing_fields}"
                        
            except json.JSONDecodeError:
                result["response_text"] = response.text[:200]
            
            if response.status_code != expected_status:
                result["error"] = f"Expected {expected_status}, got {response.status_code}"
            
        except requests.exceptions.Timeout:
            result = {
                "endpoint": path,
                "url": url,
                "success": False,
                "error": "Request timeout",
                "response_time_ms": self.timeout * 1000,
                "timestamp": datetime.utcnow().isoformat()
            }
        except requests.exceptions.RequestException as e:
            result = {
                "endpoint": path,
                "url": url,
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        
        self.results.append(result)
        return result
    
    def check_database_connectivity(self) -> Dict[str, Any]:
        """Check database connectivity through API"""
        return self.check_endpoint(
            "/health",
            required_fields=["status"]
        )
    
    def check_authentication(self) -> Dict[str, Any]:
        """Test authentication endpoints"""
        # Test demo login
        demo_result = self.check_endpoint("/demo-login")
        
        if demo_result["success"]:
            try:
                # Get demo credentials
                demo_data = demo_result["response_data"]
                username = demo_data["demo_credentials"]["username"]
                password = demo_data["demo_credentials"]["password"]
                
                # Test login
                login_url = f"{self.base_url}/users/login"
                login_data = {
                    "username": username,
                    "password": password
                }
                
                login_response = requests.post(
                    login_url, 
                    data=login_data,
                    timeout=self.timeout
                )
                
                auth_result = {
                    "endpoint": "/users/login",
                    "success": login_response.status_code == 200,
                    "status_code": login_response.status_code,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if login_response.status_code == 200:
                    token_data = login_response.json()
                    if "access_token" in token_data:
                        auth_result["token_received"] = True
                    else:
                        auth_result["success"] = False
                        auth_result["error"] = "No access token in response"
                
                self.results.append(auth_result)
                return auth_result
                
            except Exception as e:
                auth_result = {
                    "endpoint": "/users/login",
                    "success": False,
                    "error": f"Authentication test failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }
                self.results.append(auth_result)
                return auth_result
        
        return {"success": False, "error": "Demo login endpoint failed"}
    
    def check_core_functionality(self) -> List[Dict[str, Any]]:
        """Check core application functionality"""
        core_checks = [
            # Basic endpoints
            ("/health", 200, ["status"]),
            ("/docs", 200, None),
            ("/metrics", 200, None),
            
            # API structure
            ("/", 200, None),  # Should redirect to docs
        ]
        
        results = []
        for endpoint, expected_status, required_fields in core_checks:
            result = self.check_endpoint(endpoint, expected_status, required_fields)
            results.append(result)
        
        return results
    
    def check_performance(self) -> Dict[str, Any]:
        """Check application performance"""
        performance_checks = [
            "/health",
            "/metrics"
        ]
        
        response_times = []
        
        for endpoint in performance_checks:
            result = self.check_endpoint(endpoint)
            if result["success"]:
                response_times.append(result["response_time_ms"])
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            performance_result = {
                "check_type": "performance",
                "avg_response_time_ms": round(avg_response_time, 2),
                "max_response_time_ms": round(max_response_time, 2),
                "slow_endpoints": [
                    r for r in self.results[-len(performance_checks):] 
                    if r.get("response_time_ms", 0) > 2000
                ],
                "success": avg_response_time < 2000 and max_response_time < 5000,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            performance_result = {
                "check_type": "performance",
                "success": False,
                "error": "No successful requests for performance measurement",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        self.results.append(performance_result)
        return performance_result
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all health checks"""
        print(f"[CHECK] Running comprehensive health check for {self.base_url}")
        
        # Core functionality
        print("[CORE] Checking core functionality...")
        core_results = self.check_core_functionality()
        
        # Database connectivity
        print("[DB] Checking database connectivity...")
        db_result = self.check_database_connectivity()
        
        # Authentication
        print("[AUTH] Checking authentication...")
        auth_result = self.check_authentication()
        
        # Performance
        print("[PERF] Checking performance...")
        perf_result = self.check_performance()
        
        # Summary
        total_checks = len(self.results)
        successful_checks = len([r for r in self.results if r.get("success", False)])
        
        overall_success = successful_checks >= (total_checks * 0.8)  # 80% success rate
        
        summary = {
            "overall_success": overall_success,
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "success_rate": round((successful_checks / total_checks) * 100, 1) if total_checks > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": self.base_url,
            "detailed_results": self.results
        }
        
        return summary

def main():
    """Main health check execution"""
    if len(sys.argv) < 2:
        print("Usage: python health-check.py <API_URL> [timeout]")
        print("Example: python health-check.py https://ai-agent-aff6.onrender.com 30")
        sys.exit(1)
    
    api_url = sys.argv[1]
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    checker = HealthChecker(api_url, timeout)
    results = checker.run_comprehensive_check()
    
    # Print results
    print("\n" + "="*60)
    print("[RESULTS] HEALTH CHECK RESULTS")
    print("="*60)
    
    print(f"Overall Status: {'[OK] HEALTHY' if results['overall_success'] else '[ERROR] UNHEALTHY'}")
    print(f"Success Rate: {results['success_rate']}% ({results['successful_checks']}/{results['total_checks']})")
    print(f"API URL: {results['base_url']}")
    print(f"Timestamp: {results['timestamp']}")
    
    # Show failed checks
    failed_checks = [r for r in results['detailed_results'] if not r.get('success', False)]
    if failed_checks:
        print(f"\n[ERROR] FAILED CHECKS ({len(failed_checks)}):")
        for check in failed_checks:
            endpoint = check.get('endpoint', check.get('check_type', 'unknown'))
            error = check.get('error', 'Unknown error')
            print(f"  - {endpoint}: {error}")
    
    # Show slow endpoints
    slow_checks = [r for r in results['detailed_results'] 
                   if r.get('response_time_ms', 0) > 2000 and r.get('success', False)]
    if slow_checks:
        print(f"\n[WARNING] SLOW ENDPOINTS ({len(slow_checks)}):")
        for check in slow_checks:
            endpoint = check.get('endpoint', 'unknown')
            time_ms = check.get('response_time_ms', 0)
            print(f"  - {endpoint}: {time_ms}ms")
    
    # Save results to file
    results_file = f"health-check-{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[SAVE] Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_success'] else 1)

if __name__ == "__main__":
    main()