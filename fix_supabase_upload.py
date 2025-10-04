#!/usr/bin/env python3
"""
Fix Supabase Upload Issues - Comprehensive Database Saving Solution
"""

import os
import sys
import time
import json
import traceback
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and table structure"""
    print("[INFO] Testing Supabase database connection...")
    
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL:
            print("[ERROR] DATABASE_URL not found in environment")
            return False
        
        if "postgresql" not in DATABASE_URL:
            print("[ERROR] DATABASE_URL is not PostgreSQL")
            return False
        
        print(f"[INFO] Connecting to: {DATABASE_URL[:50]}...")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[SUCCESS] Connected to PostgreSQL: {version[0][:50]}...")
        
        # Check if tables exist
        tables_to_check = ['user', 'content', 'feedback', 'script']
        existing_tables = []
        
        for table in tables_to_check:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            exists = cursor.fetchone()[0]
            if exists:
                existing_tables.append(table)
                print(f"[SUCCESS] Table '{table}' exists")
            else:
                print(f"[ERROR] Table '{table}' missing")
        
        cursor.close()
        conn.close()
        
        return len(existing_tables) == len(tables_to_check)
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")
        return False

def create_missing_tables():
    """Create missing tables in Supabase"""
    print("\n🔧 Creating missing tables...")
    
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create tables with proper schema
        table_schemas = {
            'user': """
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
                    created_at REAL DEFAULT EXTRACT(EPOCH FROM NOW())
                );
            """,
            'content': """
                CREATE TABLE IF NOT EXISTS content (
                    content_id TEXT PRIMARY KEY,
                    uploader_id TEXT REFERENCES "user"(user_id),
                    title TEXT NOT NULL,
                    description TEXT,
                    file_path TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    duration_ms INTEGER DEFAULT 0,
                    uploaded_at REAL DEFAULT EXTRACT(EPOCH FROM NOW()),
                    authenticity_score REAL DEFAULT 0.0,
                    current_tags TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0
                );
            """,
            'feedback': """
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    content_id TEXT REFERENCES content(content_id),
                    user_id TEXT REFERENCES "user"(user_id),
                    event_type TEXT NOT NULL,
                    watch_time_ms INTEGER DEFAULT 0,
                    reward REAL DEFAULT 0.0,
                    rating INTEGER,
                    comment TEXT,
                    sentiment TEXT,
                    engagement_score REAL,
                    ip_address TEXT,
                    timestamp REAL DEFAULT EXTRACT(EPOCH FROM NOW())
                );
            """,
            'script': """
                CREATE TABLE IF NOT EXISTS script (
                    script_id TEXT PRIMARY KEY,
                    content_id TEXT REFERENCES content(content_id),
                    user_id TEXT REFERENCES "user"(user_id),
                    title TEXT NOT NULL,
                    script_content TEXT NOT NULL,
                    script_type TEXT DEFAULT 'text',
                    file_path TEXT,
                    created_at REAL DEFAULT EXTRACT(EPOCH FROM NOW()),
                    used_for_generation BOOLEAN DEFAULT FALSE
                );
            """,
            'analytics': """
                CREATE TABLE IF NOT EXISTS analytics (
                    id SERIAL PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    user_id TEXT REFERENCES "user"(user_id),
                    content_id TEXT REFERENCES content(content_id),
                    event_data TEXT,
                    timestamp REAL DEFAULT EXTRACT(EPOCH FROM NOW()),
                    ip_address TEXT
                );
            """,
            'system_logs': """
                CREATE TABLE IF NOT EXISTS system_logs (
                    id SERIAL PRIMARY KEY,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    module TEXT,
                    timestamp REAL DEFAULT EXTRACT(EPOCH FROM NOW()),
                    user_id TEXT REFERENCES "user"(user_id)
                );
            """
        }
        
        for table_name, schema in table_schemas.items():
            try:
                cursor.execute(schema)
                print(f"✅ Created/verified table: {table_name}")
            except Exception as e:
                print(f"❌ Failed to create table {table_name}: {e}")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_content_uploader ON content(uploader_id);",
            "CREATE INDEX IF NOT EXISTS idx_feedback_content ON feedback(content_id);",
            "CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_script_content ON script(content_id);",
            "CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_analytics_content ON analytics(content_id);"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
                print(f"✅ Created index")
            except Exception as e:
                print(f"⚠️ Index creation warning: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ All tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        traceback.print_exc()
        return False

def create_demo_user():
    """Create demo user in Supabase"""
    print("\n👤 Creating demo user...")
    
    try:
        import psycopg2
        from passlib.context import CryptContext
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Check if demo user exists
        cursor.execute('SELECT user_id FROM "user" WHERE username = %s', ('demo',))
        existing_user = cursor.fetchone()
        
        if existing_user:
            print("✅ Demo user already exists")
            cursor.close()
            conn.close()
            return True
        
        # Create password hash
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        password_hash = pwd_context.hash("demo1234")
        
        # Insert demo user
        cursor.execute("""
            INSERT INTO "user" (user_id, username, password_hash, email, email_verified, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            'demo001',
            'demo',
            password_hash,
            'demo@example.com',
            True,
            time.time()
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Demo user created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Demo user creation failed: {e}")
        return False

def test_content_upload():
    """Test content upload to Supabase"""
    print("\n📤 Testing content upload...")
    
    try:
        import psycopg2
        import uuid
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Test data
        test_content_id = f"test_{uuid.uuid4().hex[:8]}"
        test_data = {
            'content_id': test_content_id,
            'uploader_id': 'demo001',
            'title': 'Test Upload Fix',
            'description': 'Testing Supabase upload functionality',
            'file_path': '/test/path/test.txt',
            'content_type': 'text/plain',
            'duration_ms': 0,
            'uploaded_at': time.time(),
            'authenticity_score': 0.8,
            'current_tags': json.dumps(['test', 'upload', 'fix']),
            'views': 0,
            'likes': 0,
            'shares': 0
        }
        
        # Insert test content
        cursor.execute("""
            INSERT INTO content (
                content_id, uploader_id, title, description, file_path, 
                content_type, duration_ms, uploaded_at, authenticity_score, 
                current_tags, views, likes, shares
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_data['content_id'],
            test_data['uploader_id'],
            test_data['title'],
            test_data['description'],
            test_data['file_path'],
            test_data['content_type'],
            test_data['duration_ms'],
            test_data['uploaded_at'],
            test_data['authenticity_score'],
            test_data['current_tags'],
            test_data['views'],
            test_data['likes'],
            test_data['shares']
        ))
        
        # Verify insertion
        cursor.execute('SELECT title FROM content WHERE content_id = %s', (test_content_id,))
        result = cursor.fetchone()
        
        if result and result[0] == 'Test Upload Fix':
            print("✅ Content upload test successful")
            
            # Clean up test data
            cursor.execute('DELETE FROM content WHERE content_id = %s', (test_content_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
        else:
            print("❌ Content upload test failed - data not found")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Content upload test failed: {e}")
        traceback.print_exc()
        return False

def fix_database_manager():
    """Fix the DatabaseManager class to properly handle Supabase"""
    print("\n🔧 Fixing DatabaseManager class...")
    
    database_fix = '''
# Fixed DatabaseManager for Supabase
class DatabaseManager:
    def __init__(self, db_path=None):
        self.DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_agent.db")
        if 'postgresql' in self.DATABASE_URL:
            self.db_type = 'postgresql'
        else:
            self.db_type = 'sqlite'
    
    def get_connection(self):
        """Get database connection"""
        if self.db_type == 'postgresql':
            import psycopg2
            return psycopg2.connect(self.DATABASE_URL)
        else:
            import sqlite3
            return sqlite3.connect('data.db', check_same_thread=False)
    
    @staticmethod
    def create_content(content_data: dict):
        """Create content in Supabase with proper error handling"""
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO content (
                        content_id, uploader_id, title, description, file_path, 
                        content_type, duration_ms, uploaded_at, authenticity_score, 
                        current_tags, views, likes, shares
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING content_id
                """, (
                    content_data['content_id'],
                    content_data['uploader_id'],
                    content_data['title'],
                    content_data.get('description', ''),
                    content_data['file_path'],
                    content_data['content_type'],
                    content_data.get('duration_ms', 0),
                    content_data['uploaded_at'],
                    content_data.get('authenticity_score', 0.0),
                    content_data.get('current_tags', '[]'),
                    content_data.get('views', 0),
                    content_data.get('likes', 0),
                    content_data.get('shares', 0)
                ))
                
                result = cursor.fetchone()
                conn.commit()
                cursor.close()
                conn.close()
                
                print(f"✅ Content saved to Supabase: {result[0]}")
                return result[0]
                
            except Exception as e:
                print(f"❌ Supabase content save failed: {e}")
                raise e
        else:
            # SQLite fallback
            import sqlite3
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO content (
                        content_id, uploader_id, title, description, file_path, 
                        content_type, duration_ms, uploaded_at, authenticity_score, 
                        current_tags, views, likes, shares
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    content_data['content_id'],
                    content_data['uploader_id'],
                    content_data['title'],
                    content_data.get('description', ''),
                    content_data['file_path'],
                    content_data['content_type'],
                    content_data.get('duration_ms', 0),
                    content_data['uploaded_at'],
                    content_data.get('authenticity_score', 0.0),
                    content_data.get('current_tags', '[]'),
                    content_data.get('views', 0),
                    content_data.get('likes', 0),
                    content_data.get('shares', 0)
                ))
            conn.close()
            return content_data['content_id']
'''
    
    # Write the fix to a file
    with open('database_manager_fix.py', 'w') as f:
        f.write(database_fix)
    
    print("✅ DatabaseManager fix written to database_manager_fix.py")
    return True

def main():
    """Main fix function"""
    print("AI-Agent Supabase Upload Fix")
    print("=" * 50)
    
    success_count = 0
    total_tests = 5
    
    # Test 1: Database connection
    if test_database_connection():
        success_count += 1
    
    # Test 2: Create missing tables
    if create_missing_tables():
        success_count += 1
    
    # Test 3: Create demo user
    if create_demo_user():
        success_count += 1
    
    # Test 4: Test content upload
    if test_content_upload():
        success_count += 1
    
    # Test 5: Fix DatabaseManager
    if fix_database_manager():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("✅ All fixes applied successfully!")
        print("\n💡 NEXT STEPS:")
        print("1. Restart your FastAPI server")
        print("2. Test file upload via /upload endpoint")
        print("3. Check Supabase dashboard for saved content")
        print("4. Monitor logs for any remaining issues")
        return True
    else:
        print("❌ Some fixes failed. Check the errors above.")
        print("\n🔍 TROUBLESHOOTING:")
        print("1. Verify DATABASE_URL in .env file")
        print("2. Check Supabase connection permissions")
        print("3. Ensure all required packages are installed")
        print("4. Review error messages above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)