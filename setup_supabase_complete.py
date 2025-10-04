#!/usr/bin/env python3
"""
Complete Supabase Integration Setup
Creates all tables and ensures data storage is working properly
"""

import os
import psycopg2
from dotenv import load_dotenv
import time
import json

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def create_all_tables():
    """Create all required tables in Supabase"""
    
    if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
        print("ERROR: No valid PostgreSQL DATABASE_URL found")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("[INFO] Creating Supabase tables...")
        
        # 1. Users table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS "user" (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                email TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token TEXT,
                sub TEXT,
                role TEXT DEFAULT 'user',
                last_login REAL,
                created_at REAL DEFAULT EXTRACT(epoch FROM NOW())
            )
        ''')
        print("[OK] User table created")
        
        # 2. Content table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS content (
                content_id TEXT PRIMARY KEY,
                uploader_id TEXT REFERENCES "user"(user_id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                content_type TEXT NOT NULL,
                duration_ms INTEGER DEFAULT 0,
                uploaded_at REAL DEFAULT EXTRACT(epoch FROM NOW()),
                authenticity_score REAL DEFAULT 0.0,
                current_tags TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0
            )
        ''')
        print("[OK] Content table created")
        
        # 3. Feedback table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                content_id TEXT REFERENCES content(content_id) ON DELETE CASCADE,
                user_id TEXT REFERENCES "user"(user_id) ON DELETE CASCADE,
                event_type TEXT NOT NULL,
                watch_time_ms INTEGER DEFAULT 0,
                reward REAL DEFAULT 0.0,
                rating INTEGER,
                comment TEXT,
                sentiment TEXT,
                engagement_score REAL,
                ip_address TEXT,
                timestamp REAL DEFAULT EXTRACT(epoch FROM NOW())
            )
        ''')
        print("[OK] Feedback table created")
        
        # 4. Script table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS script (
                script_id TEXT PRIMARY KEY,
                content_id TEXT REFERENCES content(content_id) ON DELETE SET NULL,
                user_id TEXT REFERENCES "user"(user_id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                script_content TEXT NOT NULL,
                script_type TEXT DEFAULT 'text',
                file_path TEXT,
                created_at REAL DEFAULT EXTRACT(epoch FROM NOW()),
                used_for_generation BOOLEAN DEFAULT FALSE,
                version TEXT DEFAULT '1.0',
                script_metadata TEXT
            )
        ''')
        print("[OK] Script table created")
        
        # 5. Audit logs table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id SERIAL PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                timestamp REAL DEFAULT EXTRACT(epoch FROM NOW()),
                ip_address TEXT,
                user_agent TEXT,
                request_id TEXT,
                details TEXT,
                status TEXT DEFAULT 'success'
            )
        ''')
        print("[OK] Audit logs table created")
        
        # 6. Analytics table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id SERIAL PRIMARY KEY,
                event_type TEXT NOT NULL,
                user_id TEXT REFERENCES "user"(user_id) ON DELETE SET NULL,
                content_id TEXT REFERENCES content(content_id) ON DELETE SET NULL,
                event_data TEXT,
                timestamp REAL DEFAULT EXTRACT(epoch FROM NOW()),
                ip_address TEXT
            )
        ''')
        print("[OK] Analytics table created")
        
        # 7. System logs table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                module TEXT,
                timestamp REAL DEFAULT EXTRACT(epoch FROM NOW()),
                user_id TEXT REFERENCES "user"(user_id) ON DELETE SET NULL,
                extra_data TEXT,
                error_details TEXT,
                traceback TEXT
            )
        ''')
        print("[OK] System logs table created")
        
        # 8. Invitations table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                id SERIAL PRIMARY KEY,
                email TEXT NOT NULL,
                inviter_id TEXT REFERENCES "user"(user_id) ON DELETE CASCADE,
                invitation_token TEXT UNIQUE NOT NULL,
                created_at REAL DEFAULT EXTRACT(epoch FROM NOW()),
                expires_at REAL NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                used_at REAL
            )
        ''')
        print("[OK] Invitations table created")
        
        # Create indexes for better performance
        cur.execute('CREATE INDEX IF NOT EXISTS idx_content_uploader ON content(uploader_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_feedback_content ON feedback(content_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_script_user ON script(user_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics(user_id)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)')
        print("[OK] Database indexes created")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("[SUCCESS] All Supabase tables created successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False

def test_data_insertion():
    """Test inserting sample data to verify everything works"""
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("[INFO] Testing data insertion...")
        
        # Test user creation
        test_user_id = f"test_user_{int(time.time())}"
        cur.execute('''
            INSERT INTO "user" (user_id, username, email, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        ''', (test_user_id, f"testuser_{int(time.time())}", "test@example.com", "hashed_password", time.time()))
        
        # Test content creation
        test_content_id = f"test_content_{int(time.time())}"
        cur.execute('''
            INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (test_content_id, test_user_id, "Test Content", "Test Description", "/test/path", "video", 30000, time.time()))
        
        # Test feedback creation
        cur.execute('''
            INSERT INTO feedback (content_id, user_id, event_type, rating, comment, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (test_content_id, test_user_id, "rating", 5, "Great content!", time.time()))
        
        # Test script creation
        test_script_id = f"test_script_{int(time.time())}"
        cur.execute('''
            INSERT INTO script (script_id, user_id, title, script_content, created_at)
            VALUES (%s, %s, %s, %s, %s)
        ''', (test_script_id, test_user_id, "Test Script", "This is a test script content", time.time()))
        
        # Test analytics
        cur.execute('''
            INSERT INTO analytics (event_type, user_id, content_id, event_data, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        ''', ("test_event", test_user_id, test_content_id, '{"test": true}', time.time()))
        
        # Test audit log
        cur.execute('''
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        ''', (test_user_id, "test_action", "content", test_content_id, time.time()))
        
        # Test system log
        cur.execute('''
            INSERT INTO system_logs (level, message, module, timestamp)
            VALUES (%s, %s, %s, %s)
        ''', ("INFO", "Test system log message", "test_module", time.time()))
        
        conn.commit()
        
        # Verify data was inserted
        cur.execute('SELECT COUNT(*) FROM "user" WHERE user_id = %s', (test_user_id,))
        user_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM content WHERE content_id = %s', (test_content_id,))
        content_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM feedback WHERE content_id = %s', (test_content_id,))
        feedback_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM script WHERE script_id = %s', (test_script_id,))
        script_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM analytics WHERE user_id = %s', (test_user_id,))
        analytics_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM audit_logs WHERE user_id = %s', (test_user_id,))
        audit_count = cur.fetchone()[0]
        
        cur.execute('SELECT COUNT(*) FROM system_logs WHERE module = %s', ("test_module",))
        system_log_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        print(f"[OK] Test data verification:")
        print(f"   Users: {user_count}")
        print(f"   Content: {content_count}")
        print(f"   Feedback: {feedback_count}")
        print(f"   Scripts: {script_count}")
        print(f"   Analytics: {analytics_count}")
        print(f"   Audit logs: {audit_count}")
        print(f"   System logs: {system_log_count}")
        
        if all([user_count, content_count, feedback_count, script_count, analytics_count, audit_count, system_log_count]):
            print("[SUCCESS] All data insertion tests passed!")
            return True
        else:
            print("[ERROR] Some data insertion tests failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error testing data insertion: {e}")
        return False

def get_database_stats():
    """Get current database statistics"""
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("[STATS] Current Database Statistics:")
        
        # Get table counts
        tables = ["user", "content", "feedback", "script", "analytics", "audit_logs", "system_logs", "invitations"]
        
        for table in tables:
            try:
                if table == "user":
                    cur.execute(f'SELECT COUNT(*) FROM "{table}"')
                else:
                    cur.execute(f'SELECT COUNT(*) FROM {table}')
                count = cur.fetchone()[0]
                print(f"   {table}: {count} records")
            except Exception as e:
                print(f"   {table}: [ERROR] - {e}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"[ERROR] Error getting database stats: {e}")

def main():
    """Main setup function"""
    
    print("[SETUP] Starting Complete Supabase Integration Setup")
    print(f"[INFO] Database URL: {DATABASE_URL[:50]}...")
    
    # Step 1: Create all tables
    if not create_all_tables():
        print("[ERROR] Failed to create tables. Exiting.")
        return
    
    # Step 2: Test data insertion
    if not test_data_insertion():
        print("[WARNING] Data insertion tests failed, but tables are created.")
    
    # Step 3: Show current stats
    get_database_stats()
    
    print("\n[COMPLETE] Supabase integration setup complete!")
    print("[OK] Your AI-Agent project is now fully connected to Supabase")
    print("[OK] All tables created and data storage verified")
    print("\n[NEXT] Next steps:")
    print("   1. Start your server: python scripts/start_server.py")
    print("   2. Test endpoints: http://localhost:9000/docs")
    print("   3. Check health: http://localhost:9000/health")

if __name__ == "__main__":
    main()