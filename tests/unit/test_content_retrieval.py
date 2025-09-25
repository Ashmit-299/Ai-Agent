#!/usr/bin/env python3
"""Test content retrieval from Supabase database"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_content_retrieval():
    try:
        from core.database import DatabaseManager
        from core.models import Content
        from sqlmodel import Session, select
        
        print("Testing content retrieval from Supabase...")
        
        db = DatabaseManager()
        
        # Test database connection
        with Session(db.engine) as session:
            # Check if content table exists and has data
            statement = select(Content)
            contents = session.exec(statement).all()
            
            print(f"Found {len(contents)} content items in database")
            
            if contents:
                for content in contents[:3]:  # Show first 3
                    print(f"- ID: {content.content_id}, Title: {content.title}")
                
                # Test specific content retrieval
                test_content = contents[0]
                retrieved = db.get_content_by_id(test_content.content_id)
                
                if retrieved:
                    print(f"SUCCESS: Retrieved content {retrieved.content_id}")
                    return True
                else:
                    print("ERROR: Could not retrieve specific content")
                    return False
            else:
                print("No content found in database")
                return False
                
    except Exception as e:
        print(f"ERROR: Content retrieval failed: {e}")
        return False

if __name__ == "__main__":
    test_content_retrieval()