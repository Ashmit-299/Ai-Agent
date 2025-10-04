#!/usr/bin/env python3
"""
Fix database table conflicts and recreate properly
"""
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def fix_database_tables():
    """Fix database table conflicts"""
    try:
        print("Fixing database table conflicts...")
        
        # Remove existing database file to start fresh
        db_files = ['data.db', 'ai_agent.db', 'data.db-shm', 'data.db-wal']
        for db_file in db_files:
            if os.path.exists(db_file):
                os.remove(db_file)
                print(f"Removed {db_file}")
        
        # Import and create tables with fixed models
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("Database tables recreated successfully")
        
        # Test the models
        from core.models import User, Content, Feedback, Script, AuditLog
        print("All models imported successfully")
        
        return True
        
    except Exception as e:
        print(f"Database fix failed: {e}")
        return False

if __name__ == "__main__":
    success = fix_database_tables()
    if success:
        print("\nDatabase tables fixed successfully!")
        print("You can now start the server with: python scripts/start_server.py")
    else:
        print("\nDatabase fix failed!")
    
    sys.exit(0 if success else 1)