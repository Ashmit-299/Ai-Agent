#!/usr/bin/env python3
"""Fix the metrics endpoint by testing the analytics query directly"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_analytics_query():
    """Test the analytics query directly"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    print(f"Testing analytics query...")
    
    if 'postgresql' in DATABASE_URL:
        try:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            
            # Test each query separately
            print("Testing user count...")
            cur.execute("SELECT COUNT(*) FROM \"user\"")
            user_count = cur.fetchone()[0]
            print(f"Users: {user_count}")
            
            print("Testing content count...")
            cur.execute("SELECT COUNT(*) FROM content")
            content_count = cur.fetchone()[0]
            print(f"Content: {content_count}")
            
            print("Testing feedback count...")
            cur.execute("SELECT COUNT(*) FROM feedback")
            feedback_count = cur.fetchone()[0]
            print(f"Feedback: {feedback_count}")
            
            print("Testing average rating...")
            cur.execute("SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL")
            avg_rating = cur.fetchone()[0] or 0.0
            print(f"Average rating: {avg_rating}")
            
            print("Testing sentiment breakdown...")
            cur.execute("SELECT sentiment, COUNT(*) FROM feedback WHERE sentiment IS NOT NULL GROUP BY sentiment")
            sentiment_data = dict(cur.fetchall())
            print(f"Sentiment data: {sentiment_data}")
            
            cur.close()
            conn.close()
            
            # Test the DatabaseManager method
            print("\nTesting DatabaseManager.get_analytics_data()...")
            sys.path.append('.')
            from ..core.database import DatabaseManager
            
            analytics = DatabaseManager.get_analytics_data()
            print(f"Analytics result: {analytics}")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_analytics_query()