#!/usr/bin/env python3
"""
Connect All Supabase Tables Integration Script
Ensures all tables are properly connected and integrated with the application
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.database_integration import db_integration
from core.database import DatabaseManager, get_session
from core.models import User, Content, Script, Feedback, Analytics, SystemLog

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_database_connections():
    """Test all database table connections"""
    logger.info("Testing database table connections...")
    
    try:
        # Test basic database connection
        db_stats = db_integration.get_database_stats()
        logger.info(f"Database statistics: {db_stats}")
        
        # Test each table
        tables_status = {}
        
        # Test user table
        try:
            with next(get_session()) as session:
                from sqlmodel import select, func
                user_count = session.exec(select(func.count(User.user_id))).first()
                tables_status['user'] = {'status': 'connected', 'count': user_count}
                logger.info(f"✅ User table: {user_count} records")
        except Exception as e:
            tables_status['user'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ User table error: {e}")
        
        # Test content table
        try:
            with next(get_session()) as session:
                content_count = session.exec(select(func.count(Content.content_id))).first()
                tables_status['content'] = {'status': 'connected', 'count': content_count}
                logger.info(f"✅ Content table: {content_count} records")
        except Exception as e:
            tables_status['content'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ Content table error: {e}")
        
        # Test script table
        try:
            with next(get_session()) as session:
                script_count = session.exec(select(func.count(Script.script_id))).first()
                tables_status['script'] = {'status': 'connected', 'count': script_count}
                logger.info(f"✅ Script table: {script_count} records")
        except Exception as e:
            tables_status['script'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ Script table error: {e}")
        
        # Test feedback table
        try:
            with next(get_session()) as session:
                feedback_count = session.exec(select(func.count(Feedback.id))).first()
                tables_status['feedback'] = {'status': 'connected', 'count': feedback_count}
                logger.info(f"✅ Feedback table: {feedback_count} records")
        except Exception as e:
            tables_status['feedback'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ Feedback table error: {e}")
        
        # Test analytics table
        try:
            with next(get_session()) as session:
                analytics_count = session.exec(select(func.count(Analytics.id))).first()
                tables_status['analytics'] = {'status': 'connected', 'count': analytics_count}
                logger.info(f"✅ Analytics table: {analytics_count} records")
        except Exception as e:
            tables_status['analytics'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ Analytics table error: {e}")
        
        # Test system_logs table
        try:
            with next(get_session()) as session:
                logs_count = session.exec(select(func.count(SystemLog.id))).first()
                tables_status['system_logs'] = {'status': 'connected', 'count': logs_count}
                logger.info(f"✅ System logs table: {logs_count} records")
        except Exception as e:
            tables_status['system_logs'] = {'status': 'error', 'error': str(e)}
            logger.error(f"❌ System logs table error: {e}")
        
        return tables_status
        
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return {'error': str(e)}

def create_sample_integrated_data():
    """Create sample data to demonstrate table integration"""
    logger.info("Creating sample integrated data...")
    
    try:
        # Create sample user
        sample_user_data = {
            'user_id': f'integration_test_{int(time.time())}',
            'username': f'test_user_{int(time.time())}',
            'password_hash': 'hashed_password_sample',
            'email': f'test_{int(time.time())}@example.com',
            'email_verified': True,
            'role': 'user',
            'created_at': time.time()
        }
        
        user_result = db_integration.create_user_with_analytics(sample_user_data)
        logger.info(f"✅ Created sample user: {user_result.username}")
        
        # Create sample content with script
        sample_content_data = {
            'content_id': f'content_test_{int(time.time())}',
            'uploader_id': user_result.user_id,
            'title': 'Sample Integration Test Content',
            'description': 'This content demonstrates table integration',
            'file_path': '/tmp/sample_file.txt',
            'content_type': 'text/plain',
            'uploaded_at': time.time(),
            'authenticity_score': 0.85,
            'current_tags': json.dumps(['integration', 'test', 'sample']),
            'views': 0,
            'likes': 0,
            'shares': 0
        }
        
        sample_script_data = {
            'script_id': f'script_test_{int(time.time())}',
            'user_id': user_result.user_id,
            'title': 'Sample Integration Script',
            'script_content': 'This is a sample script for integration testing.',
            'script_type': 'integration_test',
            'created_at': time.time(),
            'used_for_generation': False
        }
        
        content_result = db_integration.create_content_with_relationships(
            sample_content_data, sample_script_data
        )
        logger.info(f"✅ Created sample content: {content_result['content'].title}")
        logger.info(f"✅ Created sample script: {content_result['script'].title}")
        
        # Create sample feedback
        sample_feedback_data = {
            'content_id': content_result['content'].content_id,
            'user_id': user_result.user_id,
            'event_type': 'like',
            'watch_time_ms': 30000,
            'reward': 1.0,
            'rating': 5,
            'comment': 'Great integration test content!',
            'sentiment': 'positive',
            'engagement_score': 0.9,
            'timestamp': time.time()
        }
        
        feedback_result = db_integration.create_feedback_with_analytics(sample_feedback_data)
        logger.info(f"✅ Created sample feedback: Rating {feedback_result.rating}")
        
        return {
            'user': user_result,
            'content': content_result,
            'feedback': feedback_result,
            'integration_test': 'success'
        }
        
    except Exception as e:
        logger.error(f"Sample data creation failed: {e}")
        return {'error': str(e)}

def main():
    """Main integration testing function"""
    logger.info("🚀 Starting Supabase Tables Integration Test")
    logger.info("=" * 60)
    
    try:
        # Test database connections
        logger.info("📊 Testing database connections...")
        tables_status = test_database_connections()
        
        # Create sample data
        logger.info("📝 Creating sample integrated data...")
        sample_data = create_sample_integrated_data()
        
        # Generate dashboard data
        logger.info("📋 Generating dashboard data...")
        dashboard_data = db_integration.get_dashboard_data()
        
        # Summary
        logger.info("=" * 60)
        logger.info("🎉 INTEGRATION TEST COMPLETE")
        logger.info("=" * 60)
        
        # Count successful connections
        successful_tables = sum(1 for status in tables_status.values() 
                              if isinstance(status, dict) and status.get('status') == 'connected')
        total_tables = len(tables_status)
        
        logger.info(f"📊 Tables Connected: {successful_tables}/{total_tables}")
        logger.info(f"📈 Dashboard Data: {len(dashboard_data)} metrics")
        
        if successful_tables == total_tables:
            logger.info("✅ ALL TABLES SUCCESSFULLY INTEGRATED!")
            return True
        else:
            logger.warning("⚠️  Some tables need attention")
            return False
            
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)