#!/usr/bin/env python3
"""Test specific content ID retrieval"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_specific_content():
    try:
        from core.database import DatabaseManager
        
        content_id = "3513a40dfe08_716896"
        print(f"Testing retrieval of content ID: {content_id}")
        
        db = DatabaseManager()
        content = db.get_content_by_id(content_id)
        
        if content:
            print(f"SUCCESS: Found content - Title: {content.title}")
            print(f"File path: {content.file_path}")
            print(f"Content type: {content.content_type}")
            return True
        else:
            print("Content not found - checking all available content IDs...")
            
            from sqlmodel import Session, select
            from core.models import Content
            
            with Session(db.engine) as session:
                statement = select(Content)
                all_contents = session.exec(statement).all()
                
                print("Available content IDs:")
                for content in all_contents:
                    print(f"- {content.content_id}: {content.title}")
                
            return False
                
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    test_specific_content()