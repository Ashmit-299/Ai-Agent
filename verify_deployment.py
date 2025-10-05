#!/usr/bin/env python3
"""
Deployment Verification Script
Comprehensive post-deployment validation for production and staging environments.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import aiohttp
import requests


class DeploymentVerifier:
    """Comprehensive deployment verification"""
    
    def __init__(self, base_url: str = None, environment: str = "production"):
        self.base_url = base_url or "https://ai-agent-aff6.onrender.com"
        self.environment = environment
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'environment': environment,
            'base_url': self.base_url,
            'tests': {},
            'summary': {'passed': 0, 'failed': 0, 'warnings': 0}
        }
        
    def log_result(self, test_name: str, status: str, message: str, details: Optional[Dict] = None):
        """Log test result"""
        self.results['tests'][test_name] = {
            'status': status,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        if status == 'PASS':
            self.results['summary']['passed'] += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.results['summary']['failed'] += 1
            print(f"❌ {test_name}: {message}")
        else:  # WARNING
            self.results['summary']['warnings'] += 1
            print(f"⚠️  {test_name}: {message}")
    
    async def test_basic_connectivity(self) -> bool:
        """Test basic server connectivity and response"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                start_time = time.time()
                async with session.get(f"{self.base_url}/health") as response:
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status == 200:
                        data = await response.json()
                        self.log_result('basic_connectivity', 'PASS', 
                                      f'Server responding ({response_time:.0f}ms)', 
                                      {'response_time_ms': response_time, 'health_data': data})
                        return True
                    else:
                        self.log_result('basic_connectivity', 'FAIL', 
                                      f'Server returned {response.status}',
                                      {'status_code': response.status, 'response_time_ms': response_time})
                        return False
                        
        except Exception as e:
            self.log_result('basic_connectivity', 'FAIL', f'Connection failed: {str(e)}')
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Test critical API endpoints"""
        endpoints = {
            '/health': 'Health check',
            '/docs': 'API documentation',
            '/openapi.json': 'OpenAPI schema',
            '/metrics': 'System metrics',
            '/demo-login': 'Demo authentication',
            '/debug-routes': 'Route enumeration'
        }
        
        endpoint_results = {}
        passed_endpoints = 0
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for endpoint, description in endpoints.items():
                try:
                    start_time = time.time()
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        endpoint_results[endpoint] = {
                            'status_code': response.status,
                            'response_time_ms': response_time,
                            'description': description,
                            'accessible': response.status < 400
                        }
                        
                        if response.status < 400:
                            passed_endpoints += 1
                            
                except Exception as e:
                    endpoint_results[endpoint] = {
                        'status_code': None,
                        'error': str(e),
                        'description': description,
                        'accessible': False
                    }
        
        success_rate = (passed_endpoints / len(endpoints)) * 100
        
        if success_rate >= 80:
            self.log_result('api_endpoints', 'PASS', 
                          f'API endpoints accessible ({passed_endpoints}/{len(endpoints)})',
                          endpoint_results)
            return True
        elif success_rate >= 60:
            self.log_result('api_endpoints', 'WARNING', 
                          f'Some API endpoints inaccessible ({passed_endpoints}/{len(endpoints)})',
                          endpoint_results)
            return False
        else:
            self.log_result('api_endpoints', 'FAIL', 
                          f'Many API endpoints failing ({passed_endpoints}/{len(endpoints)})',
                          endpoint_results)
            return False
    
    async def test_authentication_flow(self) -> bool:
        """Test authentication system"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get demo credentials
                async with session.get(f"{self.base_url}/demo-login") as response:
                    if response.status != 200:
                        self.log_result('authentication', 'FAIL', 
                                      'Demo login endpoint not accessible')
                        return False
                    
                    demo_data = await response.json()
                
                # Test login
                login_data = {
                    'username': demo_data.get('username', 'demo'),
                    'password': demo_data.get('password', 'demo1234')
                }
                
                async with session.post(
                    f"{self.base_url}/users/login",
                    data=login_data
                ) as response:
                    if response.status == 200:
                        auth_data = await response.json()
                        token = auth_data.get('access_token')
                        
                        if token:
                            # Test authenticated endpoint
                            headers = {'Authorization': f'Bearer {token}'}
                            async with session.get(
                                f"{self.base_url}/users/profile",
                                headers=headers
                            ) as profile_response:
                                
                                auth_results = {
                                    'demo_login': True,
                                    'token_received': bool(token),
                                    'profile_accessible': profile_response.status == 200
                                }
                                
                                if profile_response.status == 200:
                                    self.log_result('authentication', 'PASS', 
                                                  'Authentication flow working', auth_results)
                                    return True
                                else:
                                    self.log_result('authentication', 'WARNING', 
                                                  'Token auth partially working', auth_results)
                                    return False
                        else:
                            self.log_result('authentication', 'FAIL', 
                                          'No token received from login')
                            return False
                    else:
                        self.log_result('authentication', 'FAIL', 
                                      f'Login failed with status {response.status}')
                        return False
                        
        except Exception as e:
            self.log_result('authentication', 'FAIL', f'Authentication test error: {str(e)}')
            return False
    
    async def test_database_connectivity(self) -> bool:
        """Test database connectivity and operations"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test endpoints that require database
                db_endpoints = [
                    '/contents',
                    '/users/supabase-auth-health',
                    '/storage/status'
                ]
                
                db_results = {}
                working_endpoints = 0
                
                for endpoint in db_endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            db_results[endpoint] = {
                                'status_code': response.status,
                                'accessible': response.status < 500
                            }
                            
                            if response.status < 500:
                                working_endpoints += 1
                                
                    except Exception as e:
                        db_results[endpoint] = {
                            'error': str(e),
                            'accessible': False
                        }
                
                if working_endpoints >= 2:
                    self.log_result('database_connectivity', 'PASS', 
                                  f'Database operations working ({working_endpoints}/{len(db_endpoints)})',
                                  db_results)
                    return True
                elif working_endpoints >= 1:
                    self.log_result('database_connectivity', 'WARNING', 
                                  f'Limited database connectivity ({working_endpoints}/{len(db_endpoints)})',
                                  db_results)
                    return False
                else:
                    self.log_result('database_connectivity', 'FAIL', 
                                  'Database connectivity issues', db_results)
                    return False
                    
        except Exception as e:
            self.log_result('database_connectivity', 'FAIL', 
                          f'Database test error: {str(e)}')
            return False
    
    async def test_monitoring_systems(self) -> bool:
        """Test monitoring and observability systems"""
        try:
            monitoring_endpoints = {
                '/metrics': 'System metrics',
                '/metrics/prometheus': 'Prometheus metrics',
                '/observability/health': 'Observability health',
                '/health/detailed': 'Detailed health check'
            }
            
            monitoring_results = {}
            working_monitors = 0
            
            async with aiohttp.ClientSession() as session:
                for endpoint, description in monitoring_endpoints.items():
                    try:
                        async with session.get(f"{self.base_url}{endpoint}") as response:
                            monitoring_results[endpoint] = {
                                'status_code': response.status,
                                'description': description,
                                'working': response.status == 200
                            }
                            
                            if response.status == 200:
                                working_monitors += 1
                                
                    except Exception as e:
                        monitoring_results[endpoint] = {
                            'error': str(e),
                            'description': description,
                            'working': False
                        }
            
            monitor_rate = (working_monitors / len(monitoring_endpoints)) * 100
            
            if monitor_rate >= 75:
                self.log_result('monitoring_systems', 'PASS', 
                              f'Monitoring systems operational ({working_monitors}/{len(monitoring_endpoints)})',
                              monitoring_results)
                return True
            elif monitor_rate >= 50:
                self.log_result('monitoring_systems', 'WARNING', 
                              f'Some monitoring issues ({working_monitors}/{len(monitoring_endpoints)})',
                              monitoring_results)
                return False
            else:
                self.log_result('monitoring_systems', 'FAIL', 
                              f'Monitoring systems failing ({working_monitors}/{len(monitoring_endpoints)})',
                              monitoring_results)
                return False
                
        except Exception as e:
            self.log_result('monitoring_systems', 'FAIL', 
                          f'Monitoring test error: {str(e)}')
            return False
    
    async def test_performance_metrics(self) -> bool:
        """Test performance and response times"""
        try:
            test_endpoints = [
                '/health',
                '/metrics',
                '/contents',
                '/demo-login'
            ]
            
            performance_data = {}
            total_response_time = 0
            successful_requests = 0
            
            async with aiohttp.ClientSession() as session:
                for endpoint in test_endpoints:
                    response_times = []
                    
                    # Test each endpoint 3 times
                    for _ in range(3):
                        try:
                            start_time = time.time()
                            async with session.get(f"{self.base_url}{endpoint}") as response:
                                response_time = (time.time() - start_time) * 1000
                                
                                if response.status < 400:
                                    response_times.append(response_time)
                                    total_response_time += response_time
                                    successful_requests += 1
                                    
                        except Exception:
                            continue
                    
                    if response_times:
                        performance_data[endpoint] = {
                            'avg_response_time': sum(response_times) / len(response_times),
                            'min_response_time': min(response_times),
                            'max_response_time': max(response_times),
                            'successful_requests': len(response_times)
                        }
            
            if successful_requests > 0:
                avg_response_time = total_response_time / successful_requests
                
                performance_summary = {
                    'average_response_time_ms': avg_response_time,
                    'successful_requests': successful_requests,
                    'total_requests': len(test_endpoints) * 3,
                    'endpoint_performance': performance_data
                }
                
                if avg_response_time < 1000:  # Less than 1 second
                    self.log_result('performance_metrics', 'PASS', 
                                  f'Good performance (avg: {avg_response_time:.0f}ms)',
                                  performance_summary)
                    return True
                elif avg_response_time < 3000:  # Less than 3 seconds
                    self.log_result('performance_metrics', 'WARNING', 
                                  f'Acceptable performance (avg: {avg_response_time:.0f}ms)',
                                  performance_summary)
                    return False
                else:
                    self.log_result('performance_metrics', 'FAIL', 
                                  f'Poor performance (avg: {avg_response_time:.0f}ms)',
                                  performance_summary)
                    return False
            else:
                self.log_result('performance_metrics', 'FAIL', 
                              'No successful requests for performance testing')
                return False
                
        except Exception as e:
            self.log_result('performance_metrics', 'FAIL', 
                          f'Performance test error: {str(e)}')
            return False
    
    async def test_security_headers(self) -> bool:
        """Test security headers and HTTPS configuration"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    headers = dict(response.headers)
                    
                    security_checks = {
                        'https_used': self.base_url.startswith('https://'),
                        'cors_headers': any('cors' in k.lower() for k in headers.keys()),
                        'content_type': 'content-type' in headers,
                        'server_header': 'server' in headers
                    }
                    
                    # Check for security headers
                    security_headers = [
                        'x-content-type-options',
                        'x-frame-options',
                        'x-xss-protection',
                        'strict-transport-security'
                    ]
                    
                    present_security_headers = []
                    for header in security_headers:
                        if header in headers:
                            present_security_headers.append(header)
                    
                    security_checks['security_headers'] = present_security_headers
                    security_checks['security_header_count'] = len(present_security_headers)
                    
                    security_score = (
                        int(security_checks['https_used']) +
                        int(security_checks['cors_headers']) +
                        min(len(present_security_headers), 2)  # Max 2 points for security headers
                    )
                    
                    if security_score >= 3:
                        self.log_result('security_headers', 'PASS', 
                                      f'Good security configuration (score: {security_score}/4)',
                                      security_checks)
                        return True
                    elif security_score >= 2:
                        self.log_result('security_headers', 'WARNING', 
                                      f'Basic security configuration (score: {security_score}/4)',
                                      security_checks)
                        return False
                    else:
                        self.log_result('security_headers', 'FAIL', 
                                      f'Poor security configuration (score: {security_score}/4)',
                                      security_checks)
                        return False
                        
        except Exception as e:
            self.log_result('security_headers', 'FAIL', 
                          f'Security headers test error: {str(e)}')
            return False
    
    async def run_all_tests(self) -> Dict:
        """Run all deployment verification tests"""
        print(f"🚀 Starting Deployment Verification for {self.environment.upper()}")
        print(f"🌐 Target URL: {self.base_url}")
        print("=" * 70)
        
        # Run all tests in sequence
        tests = [
            self.test_basic_connectivity,
            self.test_api_endpoints,
            self.test_authentication_flow,
            self.test_database_connectivity,
            self.test_monitoring_systems,
            self.test_performance_metrics,
            self.test_security_headers
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                test_name = test.__name__.replace('test_', '')
                self.log_result(test_name, 'FAIL', f'Test execution error: {str(e)}')
        
        # Generate summary
        total_tests = len(self.results['tests'])
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        warnings = self.results['summary']['warnings']
        
        print("\n" + "=" * 70)
        print(f"📊 Deployment Verification Summary - {self.environment.upper()}")
        print("=" * 70)
        print(f"Target: {self.base_url}")
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Overall deployment status
        if failed == 0 and warnings <= 1:
            print(f"\n🎉 {self.environment.upper()} DEPLOYMENT: EXCELLENT - Fully operational!")
        elif failed <= 1 and warnings <= 2:
            print(f"\n✅ {self.environment.upper()} DEPLOYMENT: GOOD - Minor issues detected")
        elif failed <= 2:
            print(f"\n⚠️  {self.environment.upper()} DEPLOYMENT: NEEDS ATTENTION - Several issues found")
        else:
            print(f"\n❌ {self.environment.upper()} DEPLOYMENT: CRITICAL ISSUES - Immediate action required")
        
        return self.results
    
    def save_results(self, filename: str = None):
        """Save verification results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"deployment_verification_{self.environment}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: {filename}")


async def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deployment Verification Script')
    parser.add_argument('--url', default='https://ai-agent-aff6.onrender.com',
                       help='Base URL to test (default: production)')
    parser.add_argument('--env', default='production',
                       help='Environment name (default: production)')
    parser.add_argument('--local', action='store_true',
                       help='Test local deployment (http://localhost:9000)')
    
    args = parser.parse_args()
    
    if args.local:
        base_url = 'http://localhost:9000'
        environment = 'local'
    else:
        base_url = args.url
        environment = args.env
    
    verifier = DeploymentVerifier(base_url, environment)
    
    try:
        results = await verifier.run_all_tests()
        verifier.save_results()
        
        # Exit with appropriate code based on results
        if results['summary']['failed'] > 2:
            sys.exit(1)  # Critical issues
        elif results['summary']['failed'] > 0:
            sys.exit(2)  # Some issues
        else:
            sys.exit(0)  # Success
            
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Verification failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())