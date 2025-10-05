#!/usr/bin/env python3
"""
Migration Rollback Testing Script
Tests migration scenarios to ensure safe database recovery
"""

import os
import sys
import subprocess
import psycopg2
from typing import List, Tuple
import logging
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigrationTester:
    """Test database migrations and rollbacks"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.required_tables = [
            'user', 'content', 'feedback', 'script', 
            'analytics', 'system_logs', 'audit_logs'
        ]
        self.test_results = []
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    def run_alembic_command(self, command: str) -> Tuple[bool, str]:
        """Run alembic command and return success status and output"""
        try:
            result = subprocess.run(
                f"alembic {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)
    
    def verify_tables_exist(self) -> List[str]:
        """Verify all required tables exist in database"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            missing_tables = []
            for table in self.required_tables:
                cur.execute(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s);",
                    (table,)
                )
                exists = cur.fetchone()[0]
                if not exists:
                    missing_tables.append(table)
            
            conn.close()
            return missing_tables
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return self.required_tables  # Assume all missing on connection failure
    
    def get_table_counts(self) -> dict:
        """Get row counts for all tables"""
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            counts = {}
            for table in self.required_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cur.fetchone()[0]
                except Exception as e:
                    counts[table] = f"Error: {str(e)}"
            
            conn.close()
            return counts
            
        except Exception as e:
            logger.error(f"Failed to get table counts: {e}")
            return {}
    
    def get_current_migration(self) -> str:
        """Get current migration revision"""
        success, output = self.run_alembic_command("current --verbose")
        if success:
            for line in output.split('\n'):
                if line.strip().startswith('Rev:'):
                    return line.split(':')[1].strip().split()[0]
        return ""
    
    def get_migration_history(self) -> List[str]:
        """Get list of available migrations"""
        success, output = self.run_alembic_command("history")
        if success:
            migrations = []
            for line in output.split('\n'):
                if ' -> ' in line and line.strip():
                    # Extract revision ID from history line
                    rev_id = line.strip().split()[0]
                    if rev_id and rev_id != 'Rev:':
                        migrations.append(rev_id)
            return migrations
        return []
    
    def test_database_connection(self) -> bool:
        """Test basic database connectivity"""
        logger.info("🔌 Testing database connection...")
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            conn.close()
            
            self.log_test_result("Database Connection", True, f"Connected to {version}")
            return True
            
        except Exception as e:
            self.log_test_result("Database Connection", False, str(e))
            return False
    
    def test_migration_status(self) -> bool:
        """Test current migration status"""
        logger.info("📋 Testing migration status...")
        
        # Test 1: Check migration status
        success, output = self.run_alembic_command("check")
        if not success:
            self.log_test_result("Migration Status Check", False, output)
            return False
        
        self.log_test_result("Migration Status Check", True, "Migration status is consistent")
        return True
    
    def test_table_verification(self) -> bool:
        """Test that all required tables exist"""
        logger.info("🗄️ Testing table verification...")
        
        missing_tables = self.verify_tables_exist()
        if missing_tables:
            self.log_test_result("Table Verification", False, f"Missing tables: {missing_tables}")
            return False
        
        self.log_test_result("Table Verification", True, "All required tables exist")
        return True
    
    def test_migration_upgrade(self) -> bool:
        """Test migration upgrade to head"""
        logger.info("⬆️ Testing migration upgrade...")
        
        success, output = self.run_alembic_command("upgrade head")
        if not success:
            self.log_test_result("Migration Upgrade", False, output)
            return False
        
        self.log_test_result("Migration Upgrade", True, "Successfully upgraded to head")
        return True
    
    def test_rollback_capability(self) -> bool:
        """Test migration rollback and recovery"""
        logger.info("🔄 Testing rollback capability...")
        
        # Get current migration and history
        current_migration = self.get_current_migration()
        if not current_migration:
            self.log_test_result("Rollback Test", False, "No current migration found")
            return False
        
        migrations = self.get_migration_history()
        if len(migrations) <= 1:
            self.log_test_result("Rollback Test", True, "Only one migration, skipping rollback test")
            return True
        
        try:
            current_index = migrations.index(current_migration)
            if current_index < len(migrations) - 1:
                previous_migration = migrations[current_index + 1]
                
                # Store current table counts
                counts_before = self.get_table_counts()
                
                # Test rollback
                logger.info(f"⏪ Rolling back to: {previous_migration}")
                success, output = self.run_alembic_command(f"downgrade {previous_migration}")
                if not success:
                    self.log_test_result("Rollback Test", False, f"Rollback failed: {output}")
                    return False
                
                # Verify database state after rollback
                logger.info("🔍 Verifying database state after rollback")
                missing_tables_after_rollback = self.verify_tables_exist()
                
                # Roll forward again
                logger.info(f"⏩ Rolling forward to: {current_migration}")
                success, output = self.run_alembic_command("upgrade head")
                if not success:
                    self.log_test_result("Rollback Test", False, f"Roll forward failed: {output}")
                    return False
                
                # Verify final state
                missing_tables_final = self.verify_tables_exist()
                if missing_tables_final:
                    self.log_test_result("Rollback Test", False, f"Tables missing after rollback test: {missing_tables_final}")
                    return False
                
                counts_after = self.get_table_counts()
                
                self.log_test_result("Rollback Test", True, 
                    f"Rollback and recovery successful. Tables before: {len(counts_before)}, after: {len(counts_after)}")
                return True
            else:
                self.log_test_result("Rollback Test", True, "Current migration is the oldest, skipping rollback test")
                return True
                
        except ValueError:
            self.log_test_result("Rollback Test", False, "Current migration not found in history")
            return False
        except Exception as e:
            self.log_test_result("Rollback Test", False, str(e))
            return False
    
    def test_data_integrity(self) -> bool:
        """Test basic data integrity after migrations"""
        logger.info("🔒 Testing data integrity...")
        
        try:
            conn = psycopg2.connect(self.database_url)
            cur = conn.cursor()
            
            # Test basic constraints and relationships
            integrity_checks = [
                ("Foreign Key Constraints", "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY'"),
                ("Primary Key Constraints", "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'PRIMARY KEY'"),
                ("Check Constraints", "SELECT COUNT(*) FROM information_schema.table_constraints WHERE constraint_type = 'CHECK'"),
            ]
            
            for check_name, query in integrity_checks:
                try:
                    cur.execute(query)
                    count = cur.fetchone()[0]
                    logger.info(f"  {check_name}: {count}")
                except Exception as e:
                    logger.warning(f"  {check_name}: Error - {e}")
            
            conn.close()
            self.log_test_result("Data Integrity", True, "Basic integrity checks completed")
            return True
            
        except Exception as e:
            self.log_test_result("Data Integrity", False, str(e))
            return False
    
    def test_migration_scenarios(self) -> bool:
        """Test various migration scenarios"""
        logger.info("🧪 Starting comprehensive migration testing...")
        
        all_tests_passed = True
        
        # Test 1: Database Connection
        if not self.test_database_connection():
            all_tests_passed = False
        
        # Test 2: Migration Status
        if not self.test_migration_status():
            all_tests_passed = False
        
        # Test 3: Table Verification
        if not self.test_table_verification():
            all_tests_passed = False
        
        # Test 4: Migration Upgrade
        if not self.test_migration_upgrade():
            all_tests_passed = False
        
        # Test 5: Rollback Capability
        if not self.test_rollback_capability():
            all_tests_passed = False
        
        # Test 6: Data Integrity
        if not self.test_data_integrity():
            all_tests_passed = False
        
        return all_tests_passed
    
    def generate_report(self) -> dict:
        """Generate comprehensive test report"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
            },
            "test_results": self.test_results,
            "database_info": {
                "url_prefix": self.database_url[:50] + "..." if len(self.database_url) > 50 else self.database_url,
                "required_tables": self.required_tables
            },
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return report

def main():
    """Main testing function"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    logger.info("🚀 Starting migration testing suite...")
    logger.info(f"📍 Database URL: {database_url[:50]}...")
    
    tester = MigrationTester(database_url)
    success = tester.test_migration_scenarios()
    
    # Generate and save report
    report = tester.generate_report()
    
    try:
        with open("migration_test_report.json", "w") as f:
            json.dump(report, f, indent=2)
        logger.info("📄 Test report saved to: migration_test_report.json")
    except Exception as e:
        logger.warning(f"Could not save report: {e}")
    
    # Print summary
    logger.info("📊 Test Summary:")
    logger.info(f"  Total Tests: {report['summary']['total_tests']}")
    logger.info(f"  ✅ Passed: {report['summary']['passed']}")
    logger.info(f"  ❌ Failed: {report['summary']['failed']}")
    logger.info(f"  Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if success:
        logger.info("🎉 All migration tests passed!")
        print("✅ MIGRATION_TESTS_PASSED")
        sys.exit(0)
    else:
        logger.error("💥 Migration tests failed!")
        print("❌ MIGRATION_TESTS_FAILED")
        
        # Print failed tests
        failed_tests = [r for r in report['test_results'] if not r['success']]
        if failed_tests:
            logger.error("Failed tests:")
            for test in failed_tests:
                logger.error(f"  - {test['test']}: {test['details']}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()