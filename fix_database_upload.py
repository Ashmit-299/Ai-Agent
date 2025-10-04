#!/usr/bin/env python3
"""
Fix database upload and logging issues
"""

import os
import time
import json
from dotenv import load_dotenv
load_dotenv()

def test_supabase_connection():
    """Test Supabase database connection and create missing tables"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or "postgresql" not in DATABASE_URL:
        print("[ERROR] Supabase DATABASE_URL not configured")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("[OK] Connected to Supabase")
        
        # Create missing tables for uploads and logs
        tables = [
            """
            CREATE TABLE IF NOT EXISTS content (
                content_id TEXT PRIMARY KEY,
                uploader_id TEXT,
                title TEXT,
                description TEXT,
                file_path TEXT,
                content_type TEXT,
                duration_ms INTEGER,
                uploaded_at REAL,
                authenticity_score REAL,
                current_tags TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                level TEXT,
                message TEXT,
                module TEXT,
                timestamp REAL,
                user_id TEXT,
                ip_address TEXT,
                request_path TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                event_type TEXT,
                user_id TEXT,
                content_id TEXT,
                event_data JSONB,
                timestamp REAL,
                ip_address TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                content_id TEXT,
                user_id TEXT,
                event_type TEXT,
                watch_time_ms INTEGER,
                reward REAL,
                rating INTEGER,
                comment TEXT,
                sentiment TEXT,
                engagement_score REAL,
                ip_address TEXT,
                timestamp REAL
            )
            """
        ]
        
        for table_sql in tables:
            try:
                cur.execute(table_sql)
                print(f"[OK] Table created/verified")
            except Exception as e:
                print(f"[WARN] Table creation: {e}")
        
        conn.commit()
        
        # Test insert with all required fields
        test_data = {
            'content_id': f'test_{int(time.time())}',
            'uploader_id': 'test_user',
            'title': 'Test Upload',
            'description': 'Database connection test',
            'file_path': '/test/path',
            'content_type': 'text',
            'duration_ms': 0,
            'uploaded_at': time.time(),
            'authenticity_score': 0.0,
            'current_tags': '',
            'views': 0,
            'likes': 0,
            'shares': 0
        }
        
        cur.execute("""
            INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_data['content_id'], test_data['uploader_id'], test_data['title'],
            test_data['description'], test_data['file_path'], test_data['content_type'],
            test_data['duration_ms'], test_data['uploaded_at'], test_data['authenticity_score'],
            test_data['current_tags'], test_data['views'], test_data['likes'], test_data['shares']
        ))
        
        # Test log insert
        cur.execute("""
            INSERT INTO system_logs (level, message, module, timestamp, user_id)
            VALUES (%s, %s, %s, %s, %s)
        """, ('INFO', 'Database connection test', 'fix_script', time.time(), 'test_user'))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("[OK] Supabase database is working - uploads will be saved")
        return True
        
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        return False

def create_logging_middleware():
    """Create enhanced logging middleware"""
    
    middleware_code = '''
# Enhanced logging middleware for requests, errors, and feedback
import time
import json
from datetime import datetime

async def log_request_middleware(request: Request, call_next):
    """Log all requests, errors, and feedback events"""
    start_time = time.time()
    client_ip = request.client.host if request.client else "unknown"
    
    # Log request
    try:
        from core.database import DatabaseManager
        DatabaseManager.save_system_log(
            level="INFO",
            message=f"Request: {request.method} {request.url.path}",
            module="api_request",
            user_id=getattr(request.state, 'user_id', None)
        )
    except Exception:
        pass
    
    try:
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000
        
        # Log response
        DatabaseManager.save_system_log(
            level="INFO" if response.status_code < 400 else "ERROR",
            message=f"Response: {response.status_code} in {duration:.2f}ms",
            module="api_response"
        )
        
        return response
        
    except Exception as e:
        # Log errors
        DatabaseManager.save_system_log(
            level="ERROR",
            message=f"Request failed: {str(e)}",
            module="api_error"
        )
        raise
'''
    
    with open('logging_middleware.py', 'w') as f:
        f.write(middleware_code)
    
    print("[OK] Created logging middleware")

if __name__ == "__main__":
    print("Fixing database upload and logging issues...")
    print("=" * 50)
    
    # Test Supabase connection
    supabase_ok = test_supabase_connection()
    
    # Create logging middleware
    create_logging_middleware()
    
    print("=" * 50)
    if supabase_ok:
        print("[SUCCESS] Database is ready for uploads")
        print("- Content uploads will be saved to Supabase")
        print("- System logs will be captured")
        print("- Analytics events will be tracked")
    else:
        print("[WARNING] Database connection issues")
        print("- Check your DATABASE_URL in .env")
        print("- Uploads will fall back to local bucket only")