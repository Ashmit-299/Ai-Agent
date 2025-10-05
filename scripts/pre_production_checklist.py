#!/usr/bin/env python3
"""
Pre-Production Deployment Checklist
Comprehensive verification before production deployment
"""

import os
import sys
import requests
import json
import time
from typing import Dict, List, Any
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionReadinessChecker:
    """Check production readiness across all systems"""
    
    def __init__(self, api_base_url: str = "http://localhost:9000"):
        self.api_base_url = api_base_url
        self.checks = []
        self.overall_status = True
    
    def add_check_result(self, category: str, check_name: str, status: bool, details: str = ""):
        """Add a check result"""
        self.checks.append({
            "category": category,
            "check_name": check_name,
            "status": "PASS" if status else "FAIL",
            "passed": status,
            "details": details
        })
        if not status:
            self.overall_status = False
        logger.info(f"{'PASS' if status else 'FAIL'} {category}: {check_name}")
        if details:
            logger.info(f"    {details}")
    
    def check_environment_variables(self):
        """Check required environment variables"""
        logger.info("\nChecking Environment Variables...")
        
        required_vars = [
            "DATABASE_URL", "JWT_SECRET_KEY", "ENVIRONMENT"
        ]
        
        optional_vars = [
            "SENTRY_DSN", "POSTHOG_API_KEY", "SUPABASE_URL", 
            "SUPABASE_ANON_KEY", "MAX_UPLOAD_SIZE_MB"
        ]
        
        # Check required variables
        for var in required_vars:
            value = os.getenv(var)
            if value:
                self.add_check_result(
                    "Environment", 
                    f"{var} configured",
                    True,
                    f"Value: {value[:20]}..." if len(value) > 20 else f"Value: {value}"
                )
            else:
                self.add_check_result(
                    "Environment", 
                    f"{var} configured",
                    False,
                    "Required variable not set"
                )
        
        # Check optional variables (warnings only)
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                self.add_check_result(
                    "Environment", 
                    f"{var} configured",
                    True,
                    "Optional variable configured"
                )
            else:
                logger.warning(f"WARNING: Optional variable {var} not set")
    
    def check_database_connectivity(self):
        """Check database connection and migrations"""
        logger.info("\nChecking Database...")
        
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                self.add_check_result("Database", "Database URL configured", False)
                return
            
            if "postgresql" in database_url:
                # PostgreSQL connection check
                try:
                    import psycopg2
                    conn = psycopg2.connect(database_url)
                    cur = conn.cursor()
                    cur.execute("SELECT 1;")
                    cur.fetchone()
                    conn.close()
                    self.add_check_result("Database", "PostgreSQL connection", True)
                except Exception as e:
                    self.add_check_result("Database", "PostgreSQL connection", False, str(e))
            else:
                # SQLite connection check
                try:
                    import sqlite3
                    conn = sqlite3.connect(database_url.replace("sqlite:///", ""))
                    cur = conn.cursor()
                    cur.execute("SELECT 1;")
                    conn.close()
                    self.add_check_result("Database", "SQLite connection", True)
                except Exception as e:
                    self.add_check_result("Database", "SQLite connection", False, str(e))
            
            # Check migrations status
            try:
                result = subprocess.run(
                    "alembic current",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    self.add_check_result("Database", "Migrations status", True, result.stdout.strip())
                else:
                    self.add_check_result("Database", "Migrations status", False, result.stderr)
            except Exception as e:
                self.add_check_result("Database", "Migrations status", False, str(e))
                
        except Exception as e:
            self.add_check_result("Database", "Database connectivity", False, str(e))
    
    def check_api_endpoints(self):
        """Check critical API endpoints"""
        logger.info("\nChecking API Endpoints...")
        
        critical_endpoints = [
            ("/health", "GET", "Health check"),
            ("/health/detailed", "GET", "Detailed health"),
            ("/metrics", "GET", "Metrics endpoint"),
            ("/docs", "GET", "API documentation"),
            ("/openapi.json", "GET", "OpenAPI schema")
        ]
        
        for endpoint, method, description in critical_endpoints:
            try:
                url = f"{self.api_base_url}{endpoint}"
                response = requests.request(method, url, timeout=10)
                
                if 200 <= response.status_code < 300:
                    self.add_check_result(
                        "API", 
                        description,
                        True,
                        f"Status: {response.status_code}"
                    )
                else:
                    self.add_check_result(
                        "API", 
                        description,
                        False,
                        f"Status: {response.status_code}"
                    )
                    
            except Exception as e:
                self.add_check_result("API", description, False, str(e))
    
    def check_authentication_system(self):
        """Check authentication system"""
        logger.info("\nChecking Authentication...")
        
        try:
            # Test auth debug endpoint
            response = requests.get(f"{self.api_base_url}/debug-auth", timeout=10)
            if response.status_code == 200:
                self.add_check_result("Auth", "Auth debug endpoint", True)
            else:
                self.add_check_result("Auth", "Auth debug endpoint", False, f"Status: {response.status_code}")
            
            # Test demo login
            response = requests.get(f"{self.api_base_url}/demo-login", timeout=10)
            if response.status_code == 200:
                self.add_check_result("Auth", "Demo login available", True)
            else:
                self.add_check_result("Auth", "Demo login available", False, f"Status: {response.status_code}")
            
            # Test Supabase auth health
            response = requests.get(f"{self.api_base_url}/users/supabase-auth-health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                supabase_available = data.get("supabase_integration", {}).get("supabase_url_configured", False)
                self.add_check_result(
                    "Auth", 
                    "Supabase integration",
                    True,
                    "Available" if supabase_available else "Local auth only"
                )
            else:
                self.add_check_result("Auth", "Supabase auth health", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.add_check_result("Auth", "Authentication system", False, str(e))
    
    def check_file_upload_limits(self):
        """Check file upload and validation limits"""
        logger.info("\nChecking File Upload Configuration...")
        
        max_upload_size = os.getenv("MAX_UPLOAD_SIZE_MB", "100")
        try:
            max_size_mb = int(max_upload_size)
            if max_size_mb > 0 and max_size_mb <= 100:
                self.add_check_result(
                    "Upload", 
                    "File size limit configured",
                    True,
                    f"Max size: {max_size_mb}MB"
                )
            else:
                self.add_check_result(
                    "Upload", 
                    "File size limit configured",
                    False,
                    f"Invalid size: {max_size_mb}MB"
                )
        except ValueError:
            self.add_check_result(
                "Upload", 
                "File size limit configured",
                False,
                f"Invalid value: {max_upload_size}"
            )
        
        # Check if validation modules are available
        try:
            import magic
            self.add_check_result("Upload", "Magic library available", True, "File type detection ready")
        except ImportError:
            self.add_check_result("Upload", "Magic library available", False, "Install python-magic")
    
    def check_observability_integration(self):
        """Check observability and monitoring"""
        logger.info("\nChecking Observability...")
        
        # Check Sentry configuration
        sentry_dsn = os.getenv("SENTRY_DSN")
        if sentry_dsn:
            self.add_check_result("Observability", "Sentry configured", True, "Error tracking enabled")
        else:
            logger.warning("WARNING: Sentry not configured - errors won't be tracked")
        
        # Check PostHog configuration
        posthog_key = os.getenv("POSTHOG_API_KEY")
        if posthog_key:
            self.add_check_result("Observability", "PostHog configured", True, "Analytics enabled")
        else:
            logger.warning("WARNING: PostHog not configured - analytics disabled")
        
        # Check metrics endpoint
        try:
            response = requests.get(f"{self.api_base_url}/metrics/performance", timeout=10)
            if response.status_code == 200:
                self.add_check_result("Observability", "Performance metrics", True)
            else:
                self.add_check_result("Observability", "Performance metrics", False)
        except Exception as e:
            self.add_check_result("Observability", "Performance metrics", False, str(e))
    
    def check_security_configuration(self):
        """Check security configuration"""
        logger.info("\nChecking Security Configuration...")
        
        # Check JWT secret
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        if jwt_secret and len(jwt_secret) >= 32:
            self.add_check_result("Security", "JWT secret length", True, "Adequate length")
        else:
            self.add_check_result("Security", "JWT secret length", False, "Should be >=32 characters")
        
        # Check if HTTPS is configured (production check)
        environment = os.getenv("ENVIRONMENT", "development")
        if environment == "production":
            if self.api_base_url.startswith("https://"):
                self.add_check_result("Security", "HTTPS enabled", True)
            else:
                self.add_check_result("Security", "HTTPS enabled", False, "Production should use HTTPS")
        else:
            self.add_check_result("Security", "HTTPS check", True, "Development environment")
        
        # Check CORS configuration
        try:
            response = requests.options(f"{self.api_base_url}/health", timeout=5)
            if response.status_code in [200, 204]:
                self.add_check_result("Security", "CORS configured", True)
            else:
                self.add_check_result("Security", "CORS configured", False, "CORS preflight failed")
        except Exception as e:
            logger.warning(f"WARNING: Could not test CORS: {e}")
    
    def check_storage_backend(self):
        """Check storage backend configuration"""
        logger.info("\nChecking Storage Backend...")
        
        # Check storage configuration
        storage_backend = os.getenv("BHIV_STORAGE_BACKEND", "local")
        self.add_check_result(
            "Storage", 
            "Backend configured",
            True,
            f"Using: {storage_backend}"
        )
        
        # Check storage status endpoint
        try:
            response = requests.get(f"{self.api_base_url}/storage/status", timeout=10)
            if response.status_code == 200:
                self.add_check_result("Storage", "Storage status endpoint", True)
            else:
                self.add_check_result("Storage", "Storage status endpoint", False)
        except Exception as e:
            self.add_check_result("Storage", "Storage status endpoint", False, str(e))
    
    def run_all_checks(self) -> bool:
        """Run all production readiness checks"""
        logger.info("Starting Production Readiness Assessment")
        logger.info("="*60)
        
        self.check_environment_variables()
        self.check_database_connectivity()
        self.check_api_endpoints()
        self.check_authentication_system()
        self.check_file_upload_limits()
        self.check_observability_integration()
        self.check_security_configuration()
        self.check_storage_backend()
        
        return self.overall_status
    
    def generate_report(self):
        """Generate production readiness report"""
        logger.info("\n" + "="*80)
        logger.info("PRODUCTION READINESS REPORT")
        logger.info("="*80)
        
        # Group checks by category
        categories = {}
        for check in self.checks:
            category = check["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(check)
        
        # Print results by category
        for category, checks in categories.items():
            logger.info(f"\n{category.upper()}")
            logger.info("-" * 40)
            
            passed_count = sum(1 for check in checks if check["passed"])
            total_count = len(checks)
            
            for check in checks:
                logger.info(f"{'PASS' if check['passed'] else 'FAIL'} {check['check_name']}")
                if check['details']:
                    logger.info(f"    {check['details']}")
            
            logger.info(f"\n    Summary: {passed_count}/{total_count} checks passed")
        
        # Overall status
        total_checks = len(self.checks)
        passed_checks = sum(1 for check in self.checks if check["passed"])
        
        logger.info(f"\n" + "="*80)
        logger.info(f"OVERALL STATUS: {passed_checks}/{total_checks} checks passed")
        
        if self.overall_status:
            logger.info("PRODUCTION READY!")
            logger.info("   All critical systems are operational")
            logger.info("   System is ready for deployment")
        else:
            logger.info("NOT PRODUCTION READY")
            logger.info("   Critical issues must be resolved before deployment")
            logger.info("   Review failed checks above")
        
        logger.info("="*80)
        
        # Save report
        report_data = {
            "timestamp": time.time(),
            "overall_status": "READY" if self.overall_status else "NOT_READY",
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "categories": categories
        }
        
        with open("production-readiness-report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        logger.info("Report saved to: production-readiness-report.json")
        
        return self.overall_status

def main():
    """Main checker function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Readiness Checker")
    parser.add_argument("--api-url", default="http://localhost:9000", help="API base URL")
    args = parser.parse_args()
    
    checker = ProductionReadinessChecker(args.api_url)
    
    try:
        all_passed = checker.run_all_checks()
        success = checker.generate_report()
        
        if success:
            logger.info("Ready for production deployment!")
            sys.exit(0)
        else:
            logger.error("Production deployment blocked")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Check interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Check failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()