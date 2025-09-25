#!/usr/bin/env python3
"""
Supabase Live Integration Tests
Tests live connection and operations with Supabase database
"""

import os
import sys
import json
import time
import uuid
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

class SupabaseLiveTester:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.test_results = []
        self.test_user_id = f"test_live_{uuid.uuid4().hex[:8]}"
        
    def log_test(self, test_name, success, details=""):
        """Log test result"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "SUCCESS" if success else "ERROR"
        print(f"{status}: {test_name} - {details}")
    
    def test_database_connection(self):
        """Test basic database connection"""
        try:
            from core.database import DatabaseManager
            db = DatabaseManager()
            
            # Test connection by creating engine
            engine = db.engine
            with engine.connect() as conn:
                from sqlalchemy import text
                result = conn.execute(text("SELECT 1 as test"))
                test_value = result.fetchone()[0]
                
                if test_value == 1:
                    self.log_test("Database Connection", True, "Connection established successfully")
                    return True
                else:
                    self.log_test("Database Connection", False, "Unexpected result from test query")
                    return False
                    
        except Exception as e:
            self.log_test("Database Connection", False, f"Connection failed: {str(e)}")
            return False
    
    def test_user_operations(self):
        """Test user CRUD operations"""
        try:
            from core.database import DatabaseManager
            from app.security import hash_password
            
            db = DatabaseManager()
            
            # Create test user
            test_user_data = {
                'user_id': self.test_user_id,
                'username': f'livetest_{uuid.uuid4().hex[:6]}',
                'password_hash': hash_password('testpass123'),
                'email': f'livetest_{uuid.uuid4().hex[:6]}@example.com',
                'created_at': time.time()
            }
            
            # Test user creation
            created_user = db.create_user(test_user_data)
            if created_user:
                self.log_test("User Creation", True, f"Created user: {created_user.username}")
            else:
                self.log_test("User Creation", False, "Failed to create user")
                return False
            
            # Test user retrieval
            retrieved_user = db.get_user_by_id(self.test_user_id)
            if retrieved_user and retrieved_user.user_id == self.test_user_id:
                self.log_test("User Retrieval", True, f"Retrieved user: {retrieved_user.username}")
            else:
                self.log_test("User Retrieval", False, "Failed to retrieve user")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("User Operations", False, f"User operations failed: {str(e)}")
            return False
    
    def test_content_operations(self):
        """Test content CRUD operations"""
        try:
            from core.database import DatabaseManager
            
            db = DatabaseManager()
            
            # Create test content
            test_content_id = f"live_test_{uuid.uuid4().hex[:8]}"
            content_data = {
                'content_id': test_content_id,
                'uploader_id': self.test_user_id,
                'title': 'Live Test Content',
                'description': 'Test content for Supabase live testing',
                'file_path': '/test/path/file.txt',
                'content_type': 'text/plain',
                'authenticity_score': 0.85,
                'current_tags': json.dumps(['test', 'live', 'supabase']),
                'uploaded_at': time.time()
            }
            
            # Test content creation
            created_content = db.create_content(content_data)
            if created_content:
                self.log_test("Content Creation", True, f"Created content: {created_content.title}")
            else:
                self.log_test("Content Creation", False, "Failed to create content")
                return False
            
            # Test content retrieval
            retrieved_content = db.get_content_by_id(test_content_id)
            if retrieved_content and retrieved_content.content_id == test_content_id:
                self.log_test("Content Retrieval", True, f"Retrieved content: {retrieved_content.title}")
            else:
                self.log_test("Content Retrieval", False, "Failed to retrieve content")
                return False
            
            return True
            
        except Exception as e:
            self.log_test("Content Operations", False, f"Content operations failed: {str(e)}")
            return False
    
    def test_feedback_operations(self):
        """Test feedback CRUD operations"""
        try:
            from core.database import DatabaseManager
            
            db = DatabaseManager()
            
            # Create test feedback
            feedback_data = {
                'content_id': f"live_test_{uuid.uuid4().hex[:8]}",
                'user_id': self.test_user_id,
                'event_type': 'like',
                'rating': 4,
                'comment': 'Great live test content!',
                'reward': 0.5,
                'timestamp': time.time()
            }
            
            # Test feedback creation
            created_feedback = db.create_feedback(feedback_data)
            if created_feedback:
                self.log_test("Feedback Creation", True, f"Created feedback with rating: {created_feedback.rating}")
                return True
            else:
                self.log_test("Feedback Creation", False, "Failed to create feedback")
                return False
            
        except Exception as e:
            self.log_test("Feedback Operations", False, f"Feedback operations failed: {str(e)}")
            return False
    
    def test_analytics_data(self):
        """Test analytics data retrieval"""
        try:
            from core.database import DatabaseManager
            
            db = DatabaseManager()
            
            # Test analytics data retrieval
            analytics_data = db.get_analytics_data()
            
            if analytics_data and 'total_users' in analytics_data:
                self.log_test("Analytics Data", True, 
                            f"Retrieved analytics: {analytics_data['total_users']} users, "
                            f"{analytics_data['total_content']} content items")
                return True
            else:
                self.log_test("Analytics Data", False, "Failed to retrieve analytics data")
                return False
            
        except Exception as e:
            self.log_test("Analytics Data", False, f"Analytics failed: {str(e)}")
            return False
    
    def test_database_performance(self):
        """Test database performance with multiple operations"""
        try:
            from core.database import DatabaseManager
            
            db = DatabaseManager()
            
            start_time = time.time()
            
            # Perform multiple quick operations
            for i in range(5):
                with db.engine.connect() as conn:
                    from sqlalchemy import text
                    result = conn.execute(text("SELECT COUNT(*) FROM \"user\""))
                    user_count = result.fetchone()[0]
            
            end_time = time.time()
            duration = end_time - start_time
            
            if duration < 5.0:  # Should complete in under 5 seconds
                self.log_test("Database Performance", True, 
                            f"5 queries completed in {duration:.2f} seconds")
                return True
            else:
                self.log_test("Database Performance", False, 
                            f"Performance issue: {duration:.2f} seconds for 5 queries")
                return False
            
        except Exception as e:
            self.log_test("Database Performance", False, f"Performance test failed: {str(e)}")
            return False
    
    def test_concurrent_operations(self):
        """Test concurrent database operations"""
        try:
            import threading
            from core.database import DatabaseManager
            
            db = DatabaseManager()
            results = []
            
            def concurrent_query():
                try:
                    from sqlalchemy import text
                    with db.engine.connect() as conn:
                        result = conn.execute(text("SELECT COUNT(*) FROM \"user\""))
                        count = result.fetchone()[0]
                        results.append(count)
                except Exception as e:
                    results.append(f"Error: {e}")
            
            # Run 3 concurrent queries
            threads = []
            for i in range(3):
                thread = threading.Thread(target=concurrent_query)
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Check results
            if len(results) == 3 and all(isinstance(r, int) for r in results):
                self.log_test("Concurrent Operations", True, 
                            f"3 concurrent queries successful, results: {results}")
                return True
            else:
                self.log_test("Concurrent Operations", False, 
                            f"Concurrent operations failed, results: {results}")
                return False
            
        except Exception as e:
            self.log_test("Concurrent Operations", False, f"Concurrency test failed: {str(e)}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            from core.database import DatabaseManager
            from sqlmodel import Session, select, delete
            from core.models import User, Content, Feedback
            
            db = DatabaseManager()
            
            with Session(db.engine) as session:
                # Delete test user
                user_stmt = delete(User).where(User.user_id == self.test_user_id)
                session.exec(user_stmt)
                
                # Delete test content
                content_stmt = delete(Content).where(Content.uploader_id == self.test_user_id)
                session.exec(content_stmt)
                
                # Delete test feedback
                feedback_stmt = delete(Feedback).where(Feedback.user_id == self.test_user_id)
                session.exec(feedback_stmt)
                
                session.commit()
                
            self.log_test("Cleanup", True, "Test data cleaned up successfully")
            
        except Exception as e:
            self.log_test("Cleanup", False, f"Cleanup failed: {str(e)}")
    
    def run_all_tests(self):
        """Run all Supabase live tests"""
        print("Supabase Live Integration Tests")
        print("=" * 50)
        
        if not self.db_url:
            print("ERROR: DATABASE_URL not set")
            return False
        
        print(f"Testing database: {self.db_url[:50]}...")
        
        # Run tests in sequence
        tests = [
            self.test_database_connection,
            self.test_user_operations,
            self.test_content_operations,
            self.test_feedback_operations,
            self.test_analytics_data,
            self.test_database_performance,
            self.test_concurrent_operations
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
        
        # Cleanup
        self.cleanup_test_data()
        
        # Generate report
        self.generate_test_report(passed_tests, total_tests)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\nTest Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        return passed_tests == total_tests
    
    def generate_test_report(self, passed_tests, total_tests):
        """Generate test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database_url': self.db_url[:50] + "...",
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': (passed_tests / total_tests) * 100,
            'test_results': self.test_results
        }
        
        with open('supabase_live_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"Test report saved to supabase_live_test_report.json")

def main():
    """Main test runner"""
    tester = SupabaseLiveTester()
    success = tester.run_all_tests()
    
    if success:
        print("\nSUCCESS: All Supabase live tests passed!")
    else:
        print("\nWARNING: Some Supabase tests failed. Check the report for details.")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()