#!/usr/bin/env python3
"""
Test System Logging - Verify logs are being saved to Supabase
"""

import os
import sys
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.system_logger import system_logger, log_info, log_warning, log_error, log_user_action, log_system_event

def test_system_logging():
    """Test all logging functions"""
    print("Testing System Logging...")
    
    # Test basic logging levels
    log_info("System logging test started", "test_module")
    log_warning("This is a test warning", "test_module")
    log_error("This is a test error", "test_module", error=Exception("Test exception"))
    
    # Test user action logging
    log_user_action("test_action", "test_user_123", {"action_data": "test"})
    
    # Test system event logging
    log_system_event("test_system_event", {"event_data": "test"})
    
    # Test logging with extra data
    log_info("Test with extra data", "test_module", "test_user_456", {
        "extra_field": "extra_value",
        "number_field": 42,
        "boolean_field": True
    })
    
    print("Logging tests completed. Checking database...")
    
    # Wait a moment for logs to be saved
    time.sleep(2)
    
    # Retrieve recent logs
    recent_logs = system_logger.get_recent_logs(10)
    
    print(f"\nRetrieved {len(recent_logs)} recent logs:")
    for log in recent_logs:
        print(f"[{log['formatted_time']}] {log['level']}: {log['message']}")
        if log['module']:
            print(f"  Module: {log['module']}")
        if log['user_id']:
            print(f"  User: {log['user_id']}")
        if log['extra_data']:
            print(f"  Extra: {log['extra_data']}")
        print()
    
    return len(recent_logs) > 0

def test_database_connection():
    """Test database connection"""
    print("Testing database connection...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("[ERROR] No DATABASE_URL configured")
        return False
    
    if "postgresql" not in DATABASE_URL:
        print("[ERROR] Not using PostgreSQL database")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Check if system_logs table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'system_logs'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("[ERROR] system_logs table does not exist")
            cur.close()
            conn.close()
            return False
        
        # Check table structure
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'system_logs'
            ORDER BY ordinal_position;
        """)
        columns = cur.fetchall()
        
        print("[OK] system_logs table exists with columns:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        # Test insert (without user_id to avoid foreign key constraint)
        cur.execute("""
            INSERT INTO system_logs (level, message, module, timestamp)
            VALUES (%s, %s, %s, %s)
        """, ("INFO", "Database connection test", "test", time.time()))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("[OK] Database connection and insert test successful")
        return True
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("=== System Logging Test ===\n")
    
    # Test database connection first
    db_ok = test_database_connection()
    print()
    
    # Test logging system
    logs_ok = test_system_logging()
    
    print("\n=== Test Results ===")
    print(f"Database Connection: {'[OK]' if db_ok else '[FAILED]'}")
    print(f"System Logging: {'[OK]' if logs_ok else '[FAILED]'}")
    
    if db_ok and logs_ok:
        print("\n[SUCCESS] All tests passed! System logging is working correctly.")
    else:
        print("\n[WARNING] Some tests failed. Check the output above for details.")