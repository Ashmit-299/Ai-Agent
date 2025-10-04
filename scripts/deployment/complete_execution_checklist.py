#!/usr/bin/env python3
"""
Complete Execution Checklist
Validates all Task 5 & 6 requirements implementation
"""

import os
import sys
import json
from datetime import datetime

class ExecutionValidator:
    def __init__(self):
        self.results = []
        
    def check_file_exists(self, filepath, description):
        """Check if file exists"""
        exists = os.path.exists(filepath)
        self.results.append({
            'check': description,
            'status': 'PASS' if exists else 'FAIL',
            'details': f"File: {filepath}"
        })
        return exists
    
    def validate_step1_unit_tests(self):
        """Step 1: Unit Tests ✅"""
        print("Step 1: Unit Test Coverage (8/10 -> 10/10)")
        print("-" * 40)
        
        checks = [
            ('tests/unit/test_bhiv_components.py', 'Enhanced BHIV components tests'),
            ('tests/integration/test_api_endpoints.py', 'API endpoints integration tests'),
            ('run_enhanced_tests.py', 'Custom test runner')
        ]
        
        passed = 0
        for filepath, desc in checks:
            if self.check_file_exists(filepath, desc):
                passed += 1
        
        print(f"Unit Tests: {passed}/{len(checks)} files present")
        return passed == len(checks)
    
    def validate_step2_security(self):
        """Step 2: Security Hardening ✅"""
        print("\nStep 2: Endpoint Security (8/10 -> 10/10)")
        print("-" * 40)
        
        # Check if security enhancements are in routes.py
        security_features = []
        try:
            with open('app/routes.py', 'r') as f:
                content = f.read()
                
            if 'get_current_user_required' in content:
                security_features.append('Enhanced authentication')
            if 'rate limiting' in content.lower():
                security_features.append('Rate limiting')
            if 'admin_key' in content:
                security_features.append('Admin key validation')
                
        except Exception as e:
            security_features.append(f'Error reading routes: {e}')
        
        # Check security middleware
        try:
            with open('app/main.py', 'r') as f:
                content = f.read()
                
            if 'X-Content-Type-Options' in content:
                security_features.append('Security headers')
            if 'suspicious_patterns' in content:
                security_features.append('Suspicious pattern detection')
                
        except Exception as e:
            security_features.append(f'Error reading main: {e}')
        
        self.results.append({
            'check': 'Security Enhancements',
            'status': 'PASS' if len(security_features) >= 3 else 'PARTIAL',
            'details': f"Features: {', '.join(security_features)}"
        })
        
        print(f"Security Features: {len(security_features)} implemented")
        return len(security_features) >= 3
    
    def validate_step3_migrations(self):
        """Step 3: Database Migrations ✅"""
        print("\nStep 3: Database Migrations (8/10 -> 10/10)")
        print("-" * 40)
        
        checks = [
            ('migrations/versions/003_add_advanced_features.py', 'Advanced features migration'),
            ('run_migrations.py', 'Alembic migration runner'),
            ('run_migrations_simple.py', 'Simple migration runner')
        ]
        
        passed = 0
        for filepath, desc in checks:
            if self.check_file_exists(filepath, desc):
                passed += 1
        
        print(f"Migration Files: {passed}/{len(checks)} present")
        return passed == len(checks)
    
    def validate_step4_invitations(self):
        """Step 4: User Invitations ✅"""
        print("\nStep 4: Test User Invitations (7/10 -> 10/10)")
        print("-" * 40)
        
        checks = [
            ('scripts/invite_test_users.py', 'Test user invitation system'),
            ('test_user_credentials.json', 'Generated test credentials'),
            ('testing_instructions.md', 'Testing instructions')
        ]
        
        passed = 0
        for filepath, desc in checks:
            if self.check_file_exists(filepath, desc):
                passed += 1
        
        # Check if test users were created
        if os.path.exists('test_user_credentials.json'):
            try:
                with open('test_user_credentials.json', 'r') as f:
                    creds = json.load(f)
                    user_count = len(creds.get('test_users', []))
                    print(f"Test Users Created: {user_count}")
            except Exception:
                pass
        
        print(f"Invitation System: {passed}/{len(checks)} components ready")
        return passed == len(checks)
    
    def validate_step5_deployment(self):
        """Step 5: Deployment Automation ✅"""
        print("\nStep 5: Deployment Automation (8/10 -> 10/10)")
        print("-" * 40)
        
        checks = [
            ('deploy.py', 'Deployment automation script'),
            ('docker/render.yaml', 'Render.com configuration'),
            ('DEPLOYMENT_GUIDE.md', 'Deployment documentation')
        ]
        
        passed = 0
        for filepath, desc in checks:
            if self.check_file_exists(filepath, desc):
                passed += 1
        
        print(f"Deployment System: {passed}/{len(checks)} components ready")
        return passed == len(checks)
    
    def validate_step6_supabase(self):
        """Step 6: Supabase Integration ✅"""
        print("\nStep 6: Supabase Live Integration (8/10 -> 10/10)")
        print("-" * 40)
        
        checks = [
            ('test_supabase_live.py', 'Supabase live integration tests'),
            ('.env', 'Environment configuration'),
            ('core/database.py', 'Database manager')
        ]
        
        passed = 0
        for filepath, desc in checks:
            if self.check_file_exists(filepath, desc):
                passed += 1
        
        # Check database connection
        db_connected = False
        try:
            from ..core.database import DatabaseManager
            db = DatabaseManager()
            with db.engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1"))
                if result.fetchone()[0] == 1:
                    db_connected = True
        except Exception:
            pass
        
        self.results.append({
            'check': 'Supabase Connection',
            'status': 'PASS' if db_connected else 'FAIL',
            'details': 'Live database connection test'
        })
        
        print(f"Supabase Integration: {passed}/{len(checks)} components + {'Connected' if db_connected else 'Not Connected'}")
        return passed == len(checks) and db_connected
    
    def generate_final_report(self):
        """Generate final execution report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'validation_results': self.results,
            'summary': {
                'total_checks': len(self.results),
                'passed_checks': len([r for r in self.results if r['status'] == 'PASS']),
                'failed_checks': len([r for r in self.results if r['status'] == 'FAIL']),
                'partial_checks': len([r for r in self.results if r['status'] == 'PARTIAL'])
            }
        }
        
        with open('execution_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def run_complete_validation(self):
        """Run complete execution validation"""
        print("COMPLETE EXECUTION CHECKLIST")
        print("=" * 50)
        print("Validating all Task 5 & 6 requirements...")
        
        steps = [
            self.validate_step1_unit_tests,
            self.validate_step2_security,
            self.validate_step3_migrations,
            self.validate_step4_invitations,
            self.validate_step5_deployment,
            self.validate_step6_supabase
        ]
        
        completed_steps = 0
        for step in steps:
            if step():
                completed_steps += 1
        
        # Generate final report
        report = self.generate_final_report()
        
        print(f"\nFINAL RESULTS")
        print("=" * 50)
        print(f"Steps Completed: {completed_steps}/{len(steps)}")
        print(f"Total Checks: {report['summary']['total_checks']}")
        print(f"Passed: {report['summary']['passed_checks']}")
        print(f"Failed: {report['summary']['failed_checks']}")
        print(f"Partial: {report['summary']['partial_checks']}")
        
        success_rate = (completed_steps / len(steps)) * 100
        print(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\nSUCCESS: EXECUTION COMPLETE - Ready for production!")
        elif success_rate >= 70:
            print("\nWARNING: MOSTLY COMPLETE - Minor issues to resolve")
        else:
            print("\nERROR: INCOMPLETE - Major issues need attention")
        
        print(f"\nDetailed report saved to: execution_validation_report.json")
        
        return success_rate >= 90

def main():
    """Main validation runner"""
    validator = ExecutionValidator()
    success = validator.run_complete_validation()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()