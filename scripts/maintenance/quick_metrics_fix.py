#!/usr/bin/env python3
"""Quick fix for metrics by testing direct database queries"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_direct_queries():
    """Test direct database queries"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"Database URL: {DATABASE_URL[:50]}...")
    
    if 'postgresql' in DATABASE_URL:
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Test the exact queries used in get_analytics_data
            print("Testing user count...")
            cur.execute('SELECT COUNT(*) FROM "user"')
            user_count = cur.fetchone()[0]
            print(f"Users: {user_count}")
            
            print("Testing content count...")
            cur.execute('SELECT COUNT(*) FROM content')
            content_count = cur.fetchone()[0]
            print(f"Content: {content_count}")
            
            print("Testing feedback count...")
            cur.execute('SELECT COUNT(*) FROM feedback')
            feedback_count = cur.fetchone()[0]
            print(f"Feedback: {feedback_count}")
            
            cur.close()
            conn.close()
            
            # Now test the DatabaseManager method
            print("\nTesting DatabaseManager...")
            from ..core.database import DatabaseManager
            analytics = DatabaseManager.get_analytics_data()
            print(f"DatabaseManager result: {analytics}")
            
            return {
                'direct_users': user_count,
                'direct_content': content_count,
                'direct_feedback': feedback_count,
                'manager_result': analytics
            }
            
        except Exception as e:
            print(f"Error: {e}")
            return {'error': str(e)}

if __name__ == "__main__":
    result = test_direct_queries()
    print(f"\nFinal result: {result}")