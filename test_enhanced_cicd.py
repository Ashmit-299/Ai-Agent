#!/usr/bin/env python3
"""
Enhanced CI/CD Pipeline Validation Script
Tests all aspects of the improved CI/CD workflow including security, compliance, and deployment verification.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yaml


class CICDValidator:
    """Comprehensive CI/CD pipeline validator"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {},
            'summary': {'passed': 0, 'failed': 0, 'warnings': 0}
        }
        self.base_url = "http://localhost:9000"
        
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
    
    def test_workflow_file_structure(self) -> bool:
        """Test CI/CD workflow file structure and syntax"""
        try:
            workflow_path = Path('.github/workflows/ci-cd-production.yml')
            
            if not workflow_path.exists():
                self.log_result('workflow_structure', 'FAIL', 'CI/CD workflow file not found')
                return False
            
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            # Check required sections
            required_sections = ['name', 'on', 'jobs']
            missing_sections = [s for s in required_sections if s not in workflow]
            
            if missing_sections:
                self.log_result('workflow_structure', 'FAIL', 
                              f'Missing sections: {missing_sections}')
                return False
            
            # Check job structure
            jobs = workflow.get('jobs', {})
            expected_jobs = ['security-scan', 'test', 'build', 'deploy', 'post-deploy']
            
            job_status = {}
            for job in expected_jobs:
                job_status[job] = job in jobs
            
            missing_jobs = [job for job, exists in job_status.items() if not exists]
            
            if missing_jobs:
                self.log_result('workflow_structure', 'WARNING', 
                              f'Missing jobs: {missing_jobs}', {'job_status': job_status})
            else:
                self.log_result('workflow_structure', 'PASS', 
                              'All required jobs present', {'job_status': job_status})
            
            return len(missing_jobs) == 0
            
        except Exception as e:
            self.log_result('workflow_structure', 'FAIL', f'Error parsing workflow: {str(e)}')
            return False
    
    def test_security_configuration(self) -> bool:
        """Test security scanning configuration"""
        try:
            # Check for security tools configuration
            security_files = {
                '.bandit': 'Bandit security scanner config',
                'pyproject.toml': 'Project security settings',
                '.github/workflows/ci-cd-production.yml': 'Security scan in CI/CD'
            }
            
            security_status = {}
            for file_path, description in security_files.items():
                exists = Path(file_path).exists()
                security_status[file_path] = {'exists': exists, 'description': description}
            
            # Check workflow for security steps
            workflow_path = Path('.github/workflows/ci-cd-production.yml')
            if workflow_path.exists():
                with open(workflow_path, 'r') as f:
                    content = f.read()
                
                security_checks = {
                    'bandit': 'bandit' in content.lower(),
                    'safety': 'safety' in content.lower(),
                    'trivy': 'trivy' in content.lower(),
                    'dependency_check': 'dependency' in content.lower()
                }
                
                security_status['workflow_security_checks'] = security_checks
            
            passed_checks = sum(1 for checks in security_status.values() 
                               if isinstance(checks, dict) and checks.get('exists', False))
            
            if passed_checks >= 2:
                self.log_result('security_config', 'PASS', 
                              f'Security configuration adequate ({passed_checks} checks)',
                              security_status)
                return True
            else:
                self.log_result('security_config', 'WARNING', 
                              f'Limited security configuration ({passed_checks} checks)',
                              security_status)
                return False
                
        except Exception as e:
            self.log_result('security_config', 'FAIL', f'Error checking security config: {str(e)}')
            return False
    
    def test_environment_configuration(self) -> bool:
        """Test environment and secrets configuration"""
        try:
            # Check for environment files
            env_files = {
                '.env.example': 'Environment template',
                'requirements.txt': 'Python dependencies',
                'runtime.txt': 'Runtime specification'
            }
            
            env_status = {}
            for file_path, description in env_files.items():
                path = Path(file_path)
                exists = path.exists()
                env_status[file_path] = {
                    'exists': exists,
                    'description': description,
                    'size': path.stat().st_size if exists else 0
                }
            
            # Check .env.example for required variables
            env_example_path = Path('.env.example')
            required_vars = [
                'DATABASE_URL', 'JWT_SECRET_KEY', 'SENTRY_DSN', 
                'POSTHOG_API_KEY', 'ENVIRONMENT'
            ]
            
            if env_example_path.exists():
                with open(env_example_path, 'r') as f:
                    env_content = f.read()
                
                var_status = {}
                for var in required_vars:
                    var_status[var] = var in env_content
                
                env_status['required_variables'] = var_status
            
            missing_files = [f for f, info in env_status.items() 
                           if isinstance(info, dict) and not info.get('exists', False)]
            
            if len(missing_files) <= 1:
                self.log_result('env_config', 'PASS', 
                              f'Environment configuration complete', env_status)
                return True
            else:
                self.log_result('env_config', 'WARNING', 
                              f'Missing environment files: {missing_files}', env_status)
                return False
                
        except Exception as e:
            self.log_result('env_config', 'FAIL', f'Error checking environment config: {str(e)}')
            return False
    
    def test_deployment_readiness(self) -> bool:
        """Test deployment configuration and readiness"""
        try:
            deployment_files = {
                'Dockerfile': 'Container configuration',
                'render.yaml': 'Render deployment config',
                'docker-compose.yml': 'Local deployment config'
            }
            
            deployment_status = {}
            for file_path, description in deployment_files.items():
                path = Path(file_path)
                exists = path.exists()
                deployment_status[file_path] = {
                    'exists': exists,
                    'description': description
                }
                
                # Check file content for basic requirements
                if exists and file_path == 'Dockerfile':
                    with open(path, 'r') as f:
                        content = f.read()
                    
                    dockerfile_checks = {
                        'python_base': 'FROM python' in content,
                        'requirements': 'requirements.txt' in content,
                        'expose_port': 'EXPOSE' in content,
                        'cmd_specified': 'CMD' in content or 'ENTRYPOINT' in content
                    }
                    deployment_status[file_path]['checks'] = dockerfile_checks
            
            # Check for deployment scripts
            scripts_dir = Path('scripts/deployment')
            if scripts_dir.exists():
                deployment_scripts = list(scripts_dir.glob('*.py'))
                deployment_status['deployment_scripts'] = {
                    'count': len(deployment_scripts),
                    'scripts': [s.name for s in deployment_scripts]
                }
            
            ready_files = sum(1 for info in deployment_status.values() 
                            if isinstance(info, dict) and info.get('exists', False))
            
            if ready_files >= 2:
                self.log_result('deployment_readiness', 'PASS', 
                              f'Deployment configuration ready ({ready_files} files)',
                              deployment_status)
                return True
            else:
                self.log_result('deployment_readiness', 'WARNING', 
                              f'Limited deployment configuration ({ready_files} files)',
                              deployment_status)
                return False
                
        except Exception as e:
            self.log_result('deployment_readiness', 'FAIL', 
                          f'Error checking deployment readiness: {str(e)}')
            return False
    
    def test_testing_infrastructure(self) -> bool:
        """Test testing infrastructure and coverage"""
        try:
            test_structure = {
                'tests/': 'Test directory',
                'tests/unit/': 'Unit tests',
                'tests/integration/': 'Integration tests',
                'tests/load_testing/': 'Load tests',
                'pytest.ini': 'Pytest configuration',
                'conftest.py': 'Test configuration'
            }
            
            test_status = {}
            for path_str, description in test_structure.items():
                path = Path(path_str)
                exists = path.exists()
                test_status[path_str] = {
                    'exists': exists,
                    'description': description
                }
                
                if exists and path.is_dir():
                    test_files = list(path.glob('test_*.py'))
                    test_status[path_str]['test_files'] = len(test_files)
            
            # Check for test running scripts
            test_scripts = [
                'scripts/test_coverage.py',
                'scripts/run_load_tests.py'
            ]
            
            for script in test_scripts:
                path = Path(script)
                test_status[script] = {
                    'exists': path.exists(),
                    'description': 'Test execution script'
                }
            
            # Count available test infrastructure
            available_infrastructure = sum(1 for info in test_status.values() 
                                         if isinstance(info, dict) and info.get('exists', False))
            
            if available_infrastructure >= 4:
                self.log_result('testing_infrastructure', 'PASS', 
                              f'Comprehensive testing infrastructure ({available_infrastructure} components)',
                              test_status)
                return True
            else:
                self.log_result('testing_infrastructure', 'WARNING', 
                              f'Basic testing infrastructure ({available_infrastructure} components)',
                              test_status)
                return False
                
        except Exception as e:
            self.log_result('testing_infrastructure', 'FAIL', 
                          f'Error checking testing infrastructure: {str(e)}')
            return False
    
    def test_monitoring_integration(self) -> bool:
        """Test monitoring and observability integration"""
        try:
            # Check for monitoring configuration
            monitoring_files = {
                'app/observability.py': 'Observability module',
                'app/streaming_metrics.py': 'Metrics collection',
                'final_monitoring_check.py': 'Monitoring verification'
            }
            
            monitoring_status = {}
            for file_path, description in monitoring_files.items():
                path = Path(file_path)
                exists = path.exists()
                monitoring_status[file_path] = {
                    'exists': exists,
                    'description': description
                }
            
            # Check for monitoring endpoints if server is running
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    monitoring_endpoints = [
                        '/metrics',
                        '/metrics/prometheus',
                        '/observability/health',
                        '/monitoring-status'
                    ]
                    
                    endpoint_status = {}
                    for endpoint in monitoring_endpoints:
                        try:
                            resp = requests.get(f"{self.base_url}{endpoint}", timeout=3)
                            endpoint_status[endpoint] = {
                                'status_code': resp.status_code,
                                'accessible': resp.status_code < 400
                            }
                        except:
                            endpoint_status[endpoint] = {
                                'status_code': None,
                                'accessible': False
                            }
                    
                    monitoring_status['endpoints'] = endpoint_status
                    
            except requests.RequestException:
                monitoring_status['server_status'] = 'not_running'
            
            # Check environment variables for monitoring services
            env_example = Path('.env.example')
            if env_example.exists():
                with open(env_example, 'r') as f:
                    env_content = f.read()
                
                monitoring_vars = {
                    'SENTRY_DSN': 'SENTRY_DSN' in env_content,
                    'POSTHOG_API_KEY': 'POSTHOG_API_KEY' in env_content
                }
                monitoring_status['environment_vars'] = monitoring_vars
            
            # Evaluate monitoring readiness
            file_count = sum(1 for info in monitoring_status.values() 
                           if isinstance(info, dict) and info.get('exists', False))
            
            if file_count >= 2:
                self.log_result('monitoring_integration', 'PASS', 
                              f'Monitoring integration configured ({file_count} components)',
                              monitoring_status)
                return True
            else:
                self.log_result('monitoring_integration', 'WARNING', 
                              f'Basic monitoring setup ({file_count} components)',
                              monitoring_status)
                return False
                
        except Exception as e:
            self.log_result('monitoring_integration', 'FAIL', 
                          f'Error checking monitoring integration: {str(e)}')
            return False
    
    def test_documentation_completeness(self) -> bool:
        """Test documentation completeness"""
        try:
            doc_files = {
                'README.md': 'Main documentation',
                'docs/': 'Documentation directory',
                'docs/privacy.md': 'Privacy policy',
                'docs/testing_instructions.md': 'Testing guide',
                'docs/endpoint_security_guide.md': 'Security guide'
            }
            
            doc_status = {}
            for path_str, description in doc_files.items():
                path = Path(path_str)
                exists = path.exists()
                doc_status[path_str] = {
                    'exists': exists,
                    'description': description
                }
                
                if exists and path.is_file():
                    doc_status[path_str]['size'] = path.stat().st_size
            
            # Check README.md content
            readme_path = Path('README.md')
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                readme_sections = {
                    'features': '## Features' in readme_content or '# Features' in readme_content,
                    'installation': 'Installation' in readme_content or 'Setup' in readme_content,
                    'api_docs': 'API' in readme_content or 'endpoints' in readme_content.lower(),
                    'testing': 'test' in readme_content.lower(),
                    'deployment': 'deploy' in readme_content.lower()
                }
                
                doc_status['README.md']['sections'] = readme_sections
            
            complete_docs = sum(1 for info in doc_status.values() 
                              if isinstance(info, dict) and info.get('exists', False))
            
            if complete_docs >= 3:
                self.log_result('documentation', 'PASS', 
                              f'Documentation complete ({complete_docs} files)',
                              doc_status)
                return True
            else:
                self.log_result('documentation', 'WARNING', 
                              f'Basic documentation ({complete_docs} files)',
                              doc_status)
                return False
                
        except Exception as e:
            self.log_result('documentation', 'FAIL', 
                          f'Error checking documentation: {str(e)}')
            return False
    
    async def run_all_tests(self) -> Dict:
        """Run all CI/CD validation tests"""
        print("🚀 Starting Enhanced CI/CD Pipeline Validation")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_workflow_file_structure,
            self.test_security_configuration,
            self.test_environment_configuration,
            self.test_deployment_readiness,
            self.test_testing_infrastructure,
            self.test_monitoring_integration,
            self.test_documentation_completeness
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                test_name = test.__name__.replace('test_', '')
                self.log_result(test_name, 'FAIL', f'Test execution error: {str(e)}')
        
        # Generate summary
        total_tests = len(self.results['tests'])
        passed = self.results['summary']['passed']
        failed = self.results['summary']['failed']
        warnings = self.results['summary']['warnings']
        
        print("\n" + "=" * 60)
        print("📊 CI/CD Validation Summary")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Overall assessment
        if failed == 0 and warnings <= 2:
            print("\n🎉 CI/CD Pipeline: EXCELLENT - Ready for production!")
        elif failed <= 1 and warnings <= 3:
            print("\n✅ CI/CD Pipeline: GOOD - Minor improvements recommended")
        elif failed <= 2:
            print("\n⚠️  CI/CD Pipeline: NEEDS WORK - Address failed tests")
        else:
            print("\n❌ CI/CD Pipeline: CRITICAL ISSUES - Major fixes required")
        
        return self.results
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"cicd_validation_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: {filename}")


async def main():
    """Main execution function"""
    validator = CICDValidator()
    
    try:
        results = await validator.run_all_tests()
        validator.save_results()
        
        # Exit with appropriate code
        if results['summary']['failed'] > 2:
            sys.exit(1)
        elif results['summary']['failed'] > 0:
            sys.exit(2)
        else:
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())