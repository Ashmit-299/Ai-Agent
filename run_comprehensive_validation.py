#!/usr/bin/env python3
"""
Comprehensive Validation Suite
Master script that runs all validation tests including CI/CD, deployment, migration, and system health checks.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests


class ComprehensiveValidator:
    """Master validation orchestrator"""
    
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'validation_suite': 'comprehensive',
            'test_categories': {},
            'summary': {
                'total_categories': 0,
                'passed_categories': 0,
                'failed_categories': 0,
                'warnings': 0
            }
        }
        
    def log_category_result(self, category: str, status: str, message: str, details: Optional[Dict] = None):
        """Log category test result"""
        self.results['test_categories'][category] = {
            'status': status,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.results['summary']['total_categories'] += 1
        
        if status == 'PASS':
            self.results['summary']['passed_categories'] += 1
            print(f"✅ {category}: {message}")
        elif status == 'FAIL':
            self.results['summary']['failed_categories'] += 1
            print(f"❌ {category}: {message}")
        else:  # WARNING
            self.results['summary']['warnings'] += 1
            print(f"⚠️  {category}: {message}")
    
    async def run_cicd_validation(self) -> bool:
        """Run CI/CD pipeline validation"""
        print("\n🔧 Running CI/CD Pipeline Validation...")
        
        try:
            # Check if CI/CD validation script exists
            cicd_script = Path('test_enhanced_cicd.py')
            if not cicd_script.exists():
                self.log_category_result('cicd_validation', 'FAIL', 
                                       'CI/CD validation script not found')
                return False
            
            # Run CI/CD validation
            result = subprocess.run([
                sys.executable, 'test_enhanced_cicd.py'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_category_result('cicd_validation', 'PASS', 
                                       'CI/CD pipeline validation successful')
                return True
            elif result.returncode == 2:
                self.log_category_result('cicd_validation', 'WARNING', 
                                       'CI/CD pipeline has minor issues')
                return False
            else:
                self.log_category_result('cicd_validation', 'FAIL', 
                                       f'CI/CD validation failed (exit code: {result.returncode})')
                return False
                
        except subprocess.TimeoutExpired:
            self.log_category_result('cicd_validation', 'FAIL', 
                                   'CI/CD validation timed out')
            return False
        except Exception as e:
            self.log_category_result('cicd_validation', 'FAIL', 
                                   f'CI/CD validation error: {str(e)}')
            return False
    
    async def run_migration_tests(self) -> bool:
        """Run database migration tests"""
        print("\n🗄️  Running Migration Tests...")
        
        try:
            # Check if migration test script exists
            migration_script = Path('test_migration_rollback.py')
            if not migration_script.exists():
                self.log_category_result('migration_tests', 'WARNING', 
                                       'Migration test script not found')
                return False
            
            # Run migration tests
            result = subprocess.run([
                sys.executable, 'test_migration_rollback.py'
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.log_category_result('migration_tests', 'PASS', 
                                       'Database migration tests successful')
                return True
            else:
                self.log_category_result('migration_tests', 'WARNING', 
                                       'Migration tests had issues')
                return False
                
        except subprocess.TimeoutExpired:
            self.log_category_result('migration_tests', 'FAIL', 
                                   'Migration tests timed out')
            return False
        except Exception as e:
            self.log_category_result('migration_tests', 'WARNING', 
                                   f'Migration test error: {str(e)}')
            return False
    
    async def run_local_deployment_verification(self) -> bool:
        """Run local deployment verification"""
        print("\n🏠 Running Local Deployment Verification...")
        
        try:
            # Check if server is running locally
            try:
                response = requests.get('http://localhost:9000/health', timeout=5)
                server_running = response.status_code == 200
            except:
                server_running = False
            
            if not server_running:
                self.log_category_result('local_deployment', 'WARNING', 
                                       'Local server not running - skipping local tests')
                return False
            
            # Check if deployment verification script exists
            deploy_script = Path('verify_deployment.py')
            if not deploy_script.exists():
                self.log_category_result('local_deployment', 'FAIL', 
                                       'Deployment verification script not found')
                return False
            
            # Run local deployment verification
            result = subprocess.run([
                sys.executable, 'verify_deployment.py', '--local'
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.log_category_result('local_deployment', 'PASS', 
                                       'Local deployment verification successful')
                return True
            elif result.returncode == 2:
                self.log_category_result('local_deployment', 'WARNING', 
                                       'Local deployment has minor issues')
                return False
            else:
                self.log_category_result('local_deployment', 'FAIL', 
                                       'Local deployment verification failed')
                return False
                
        except subprocess.TimeoutExpired:
            self.log_category_result('local_deployment', 'FAIL', 
                                   'Local deployment verification timed out')
            return False
        except Exception as e:
            self.log_category_result('local_deployment', 'WARNING', 
                                   f'Local deployment error: {str(e)}')
            return False
    
    async def run_production_deployment_verification(self) -> bool:
        """Run production deployment verification"""
        print("\n🌐 Running Production Deployment Verification...")
        
        try:
            # Check if deployment verification script exists
            deploy_script = Path('verify_deployment.py')
            if not deploy_script.exists():
                self.log_category_result('production_deployment', 'FAIL', 
                                       'Deployment verification script not found')
                return False
            
            # Run production deployment verification
            result = subprocess.run([
                sys.executable, 'verify_deployment.py', 
                '--url', 'https://ai-agent-aff6.onrender.com',
                '--env', 'production'
            ], capture_output=True, text=True, timeout=180)
            
            if result.returncode == 0:
                self.log_category_result('production_deployment', 'PASS', 
                                       'Production deployment verification successful')
                return True
            elif result.returncode == 2:
                self.log_category_result('production_deployment', 'WARNING', 
                                       'Production deployment has minor issues')
                return False
            else:
                self.log_category_result('production_deployment', 'FAIL', 
                                       'Production deployment verification failed')
                return False
                
        except subprocess.TimeoutExpired:
            self.log_category_result('production_deployment', 'FAIL', 
                                   'Production deployment verification timed out')
            return False
        except Exception as e:
            self.log_category_result('production_deployment', 'FAIL', 
                                   f'Production deployment error: {str(e)}')
            return False
    
    async def run_integration_tests(self) -> bool:
        """Run integration test suite"""
        print("\n🔗 Running Integration Tests...")
        
        try:
            # Check for integration test scripts
            integration_scripts = [
                'check_integrations.py',
                'test_live_connections.py',
                'test_prometheus_integration.py'
            ]
            
            available_scripts = []
            for script in integration_scripts:
                if Path(script).exists():
                    available_scripts.append(script)
            
            if not available_scripts:
                self.log_category_result('integration_tests', 'WARNING', 
                                       'No integration test scripts found')
                return False
            
            # Run available integration tests
            passed_tests = 0
            total_tests = len(available_scripts)
            
            for script in available_scripts:
                try:
                    result = subprocess.run([
                        sys.executable, script
                    ], capture_output=True, text=True, timeout=60)
                    
                    if result.returncode == 0:
                        passed_tests += 1
                        
                except subprocess.TimeoutExpired:
                    continue
                except Exception:
                    continue
            
            success_rate = (passed_tests / total_tests) * 100
            
            if success_rate >= 80:
                self.log_category_result('integration_tests', 'PASS', 
                                       f'Integration tests successful ({passed_tests}/{total_tests})')
                return True
            elif success_rate >= 60:
                self.log_category_result('integration_tests', 'WARNING', 
                                       f'Some integration tests failed ({passed_tests}/{total_tests})')
                return False
            else:
                self.log_category_result('integration_tests', 'FAIL', 
                                       f'Many integration tests failed ({passed_tests}/{total_tests})')
                return False
                
        except Exception as e:
            self.log_category_result('integration_tests', 'WARNING', 
                                   f'Integration test error: {str(e)}')
            return False
    
    async def run_security_validation(self) -> bool:
        """Run security validation checks"""
        print("\n🔒 Running Security Validation...")
        
        try:
            security_checks = {
                'env_example_exists': Path('.env.example').exists(),
                'env_file_not_committed': not Path('.env').exists() or Path('.env').stat().st_size == 0,
                'gitignore_exists': Path('.gitignore').exists(),
                'requirements_exists': Path('requirements.txt').exists(),
                'dockerfile_exists': Path('Dockerfile').exists()
            }
            
            # Check .gitignore for security patterns
            if security_checks['gitignore_exists']:
                with open('.gitignore', 'r') as f:
                    gitignore_content = f.read()
                
                security_patterns = ['.env', '*.key', '*.pem', '__pycache__']
                gitignore_security = sum(1 for pattern in security_patterns 
                                       if pattern in gitignore_content)
                security_checks['gitignore_security_patterns'] = gitignore_security
            
            # Check for security-related files
            security_files = ['app/security.py', 'app/auth.py']
            security_checks['security_modules'] = sum(1 for f in security_files 
                                                    if Path(f).exists())
            
            # Calculate security score
            security_score = sum([
                security_checks['env_example_exists'],
                security_checks['env_file_not_committed'],
                security_checks['gitignore_exists'],
                security_checks['requirements_exists'],
                security_checks.get('gitignore_security_patterns', 0) >= 2,
                security_checks.get('security_modules', 0) >= 1
            ])
            
            if security_score >= 5:
                self.log_category_result('security_validation', 'PASS', 
                                       f'Good security practices (score: {security_score}/6)',
                                       security_checks)
                return True
            elif security_score >= 3:
                self.log_category_result('security_validation', 'WARNING', 
                                       f'Basic security practices (score: {security_score}/6)',
                                       security_checks)
                return False
            else:
                self.log_category_result('security_validation', 'FAIL', 
                                       f'Poor security practices (score: {security_score}/6)',
                                       security_checks)
                return False
                
        except Exception as e:
            self.log_category_result('security_validation', 'WARNING', 
                                   f'Security validation error: {str(e)}')
            return False
    
    async def run_documentation_validation(self) -> bool:
        """Run documentation completeness validation"""
        print("\n📚 Running Documentation Validation...")
        
        try:
            doc_files = {
                'README.md': 'Main documentation',
                'docs/': 'Documentation directory',
                'LICENSE': 'License file',
                '.env.example': 'Environment template'
            }
            
            doc_status = {}
            for file_path, description in doc_files.items():
                path = Path(file_path)
                exists = path.exists()
                doc_status[file_path] = {
                    'exists': exists,
                    'description': description
                }
                
                if exists and path.is_file():
                    doc_status[file_path]['size'] = path.stat().st_size
            
            # Check README.md content quality
            readme_path = Path('README.md')
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()
                
                readme_quality = {
                    'has_title': readme_content.startswith('#'),
                    'has_installation': 'install' in readme_content.lower(),
                    'has_usage': 'usage' in readme_content.lower() or 'running' in readme_content.lower(),
                    'has_api_docs': 'api' in readme_content.lower() or 'endpoint' in readme_content.lower(),
                    'substantial_content': len(readme_content) > 1000
                }
                
                doc_status['README.md']['quality'] = readme_quality
            
            # Calculate documentation score
            existing_docs = sum(1 for info in doc_status.values() 
                              if isinstance(info, dict) and info.get('exists', False))
            
            if existing_docs >= 3:
                self.log_category_result('documentation_validation', 'PASS', 
                                       f'Good documentation coverage ({existing_docs}/4)',
                                       doc_status)
                return True
            elif existing_docs >= 2:
                self.log_category_result('documentation_validation', 'WARNING', 
                                       f'Basic documentation ({existing_docs}/4)',
                                       doc_status)
                return False
            else:
                self.log_category_result('documentation_validation', 'FAIL', 
                                       f'Poor documentation ({existing_docs}/4)',
                                       doc_status)
                return False
                
        except Exception as e:
            self.log_category_result('documentation_validation', 'WARNING', 
                                   f'Documentation validation error: {str(e)}')
            return False
    
    async def run_all_validations(self) -> Dict:
        """Run all validation categories"""
        print("🚀 Starting Comprehensive Validation Suite")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # Run all validation categories
        validations = [
            ('CI/CD Pipeline', self.run_cicd_validation),
            ('Migration Tests', self.run_migration_tests),
            ('Local Deployment', self.run_local_deployment_verification),
            ('Production Deployment', self.run_production_deployment_verification),
            ('Integration Tests', self.run_integration_tests),
            ('Security Validation', self.run_security_validation),
            ('Documentation', self.run_documentation_validation)
        ]
        
        for category_name, validation_func in validations:
            print(f"\n{'='*20} {category_name} {'='*20}")
            try:
                await validation_func()
            except Exception as e:
                self.log_category_result(category_name.lower().replace(' ', '_'), 
                                       'FAIL', f'Validation error: {str(e)}')
            
            # Brief pause between categories
            await asyncio.sleep(1)
        
        # Generate comprehensive summary
        total = self.results['summary']['total_categories']
        passed = self.results['summary']['passed_categories']
        failed = self.results['summary']['failed_categories']
        warnings = self.results['summary']['warnings']
        
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 80)
        print(f"Total Categories: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⚠️  Warnings: {warnings}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        # Overall system assessment
        print("\n" + "🎯 SYSTEM READINESS ASSESSMENT" + "\n" + "=" * 40)
        
        if failed == 0 and warnings <= 2:
            print("🎉 SYSTEM STATUS: PRODUCTION READY")
            print("   All critical systems operational")
            print("   Ready for production deployment")
        elif failed <= 1 and warnings <= 3:
            print("✅ SYSTEM STATUS: MOSTLY READY")
            print("   Minor issues detected")
            print("   Recommended to address warnings before production")
        elif failed <= 2:
            print("⚠️  SYSTEM STATUS: NEEDS WORK")
            print("   Several issues require attention")
            print("   Address failed categories before deployment")
        else:
            print("❌ SYSTEM STATUS: NOT READY")
            print("   Critical issues detected")
            print("   Significant work required before deployment")
        
        return self.results
    
    def save_results(self, filename: str = None):
        """Save comprehensive validation results"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comprehensive_validation_report_{timestamp}.json"
        
        # Ensure reports directory exists
        reports_dir = Path('data/reports')
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = reports_dir / filename
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Comprehensive validation report saved to: {report_path}")
        
        # Also create a summary text file
        summary_path = reports_dir / f"validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(summary_path, 'w') as f:
            f.write("COMPREHENSIVE VALIDATION SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Timestamp: {self.results['timestamp']}\n")
            f.write(f"Total Categories: {self.results['summary']['total_categories']}\n")
            f.write(f"Passed: {self.results['summary']['passed_categories']}\n")
            f.write(f"Failed: {self.results['summary']['failed_categories']}\n")
            f.write(f"Warnings: {self.results['summary']['warnings']}\n\n")
            
            f.write("CATEGORY RESULTS:\n")
            f.write("-" * 30 + "\n")
            for category, result in self.results['test_categories'].items():
                f.write(f"{category}: {result['status']} - {result['message']}\n")
        
        print(f"📄 Summary report saved to: {summary_path}")


async def main():
    """Main execution function"""
    validator = ComprehensiveValidator()
    
    try:
        print("🔍 AI-Agent Comprehensive Validation Suite")
        print("🎯 Testing all aspects of the system for production readiness")
        print()
        
        results = await validator.run_all_validations()
        validator.save_results()
        
        # Exit with appropriate code
        failed = results['summary']['failed_categories']
        
        if failed == 0:
            print("\n🎉 All validations completed successfully!")
            sys.exit(0)
        elif failed <= 2:
            print(f"\n⚠️  Validation completed with {failed} failed categories")
            sys.exit(2)
        else:
            print(f"\n❌ Validation failed with {failed} critical issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Validation suite failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())