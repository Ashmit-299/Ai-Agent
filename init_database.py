#!/usr/bin/env python3
"""
Complete Database Initialization Script
Creates all required tables for all endpoints
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Fix psycopg2 import
try:
    import psycopg2
except ImportError:
    try:
        import psycopg2_binary as psycopg2
        sys.modules['psycopg2'] = psycopg2
    except ImportError:
        pass

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/data.db")

def init_postgresql():
    """Initialize PostgreSQL database with all tables"""
    import psycopg2
    
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Create all tables
    tables = [
        # Users table
        '''CREATE TABLE IF NOT EXISTS "user" (
            user_id VARCHAR PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR,
            email VARCHAR,
            email_verified BOOLEAN DEFAULT FALSE,
            verification_token VARCHAR,
            sub VARCHAR,
            role VARCHAR DEFAULT 'user',
            last_login FLOAT,
            created_at FLOAT NOT NULL
        )''',
        
        # Content table
        '''CREATE TABLE IF NOT EXISTS content (
            content_id VARCHAR PRIMARY KEY,
            uploader_id VARCHAR REFERENCES "user"(user_id),
            title VARCHAR NOT NULL,
            description TEXT,
            file_path VARCHAR NOT NULL,
            content_type VARCHAR NOT NULL,
            duration_ms INTEGER DEFAULT 0,
            uploaded_at FLOAT NOT NULL,
            authenticity_score FLOAT DEFAULT 0.0,
            current_tags TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0
        )''',
        
        # Feedback table
        '''CREATE TABLE IF NOT EXISTS feedback (
            id SERIAL PRIMARY KEY,
            content_id VARCHAR REFERENCES content(content_id),
            user_id VARCHAR REFERENCES "user"(user_id),
            event_type VARCHAR NOT NULL,
            watch_time_ms INTEGER DEFAULT 0,
            reward FLOAT DEFAULT 0.0,
            rating INTEGER,
            comment TEXT,
            sentiment VARCHAR,
            engagement_score FLOAT,
            ip_address VARCHAR,
            timestamp FLOAT NOT NULL
        )''',
        
        # Script table
        '''CREATE TABLE IF NOT EXISTS script (
            script_id VARCHAR PRIMARY KEY,
            content_id VARCHAR REFERENCES content(content_id),
            user_id VARCHAR REFERENCES "user"(user_id),
            title VARCHAR NOT NULL,
            script_content TEXT NOT NULL,
            script_type VARCHAR DEFAULT 'text',
            file_path VARCHAR,
            created_at FLOAT NOT NULL,
            used_for_generation BOOLEAN DEFAULT FALSE,
            version VARCHAR DEFAULT '1.0',
            script_metadata TEXT
        )''',
        
        # Audit logs table
        '''CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR,
            action VARCHAR NOT NULL,
            resource_type VARCHAR NOT NULL,
            resource_id VARCHAR NOT NULL,
            timestamp FLOAT NOT NULL,
            ip_address VARCHAR,
            user_agent TEXT,
            request_id VARCHAR,
            details TEXT,
            status VARCHAR DEFAULT 'success'
        )''',
        
        # Analytics table
        '''CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            event_type VARCHAR NOT NULL,
            user_id VARCHAR REFERENCES "user"(user_id),
            content_id VARCHAR REFERENCES content(content_id),
            event_data TEXT,
            timestamp FLOAT NOT NULL,
            ip_address VARCHAR
        )''',
        
        # System logs table
        '''CREATE TABLE IF NOT EXISTS system_logs (
            id SERIAL PRIMARY KEY,
            level VARCHAR NOT NULL,
            message TEXT NOT NULL,
            module VARCHAR,
            timestamp FLOAT NOT NULL,
            user_id VARCHAR REFERENCES "user"(user_id),
            extra_data TEXT,
            error_details TEXT,
            traceback TEXT
        )''',
        
        # Invitations table
        '''CREATE TABLE IF NOT EXISTS invitations (
            id SERIAL PRIMARY KEY,
            email VARCHAR NOT NULL,
            inviter_id VARCHAR REFERENCES "user"(user_id),
            invitation_token VARCHAR UNIQUE NOT NULL,
            created_at FLOAT NOT NULL,
            expires_at FLOAT NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            used_at FLOAT
        )'''
    ]
    
    for i, table_sql in enumerate(tables, 1):
        try:
            cur.execute(table_sql)
            print(f"[OK] Table {i}/8 created/verified")
        except Exception as e:
            print(f"[ERROR] Table {i}/8 failed: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("\n[SUCCESS] PostgreSQL database initialized successfully!")

def init_sqlite():
    """Initialize SQLite database with all tables"""
    import sqlite3
    
    db_path = DATABASE_URL.replace("sqlite:///", "")
    os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Create all tables
    tables = [
        '''CREATE TABLE IF NOT EXISTS "user" (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            email TEXT,
            email_verified INTEGER DEFAULT 0,
            verification_token TEXT,
            sub TEXT,
            role TEXT DEFAULT 'user',
            last_login REAL,
            created_at REAL NOT NULL
        )''',
        
        '''CREATE TABLE IF NOT EXISTS content (
            content_id TEXT PRIMARY KEY,
            uploader_id TEXT REFERENCES "user"(user_id),
            title TEXT NOT NULL,
            description TEXT,
            file_path TEXT NOT NULL,
            content_type TEXT NOT NULL,
            duration_ms INTEGER DEFAULT 0,
            uploaded_at REAL NOT NULL,
            authenticity_score REAL DEFAULT 0.0,
            current_tags TEXT,
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0
        )''',
        
        '''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            timestamp REAL NOT NULL
        )''',
        
        '''CREATE TABLE IF NOT EXISTS script (
            script_id TEXT PRIMARY KEY,
            content_id TEXT REFERENCES content(content_id),
            user_id TEXT REFERENCES "user"(user_id),
            title TEXT NOT NULL,
            script_content TEXT NOT NULL,
            script_type TEXT DEFAULT 'text',
            file_path TEXT,
            created_at REAL NOT NULL,
            used_for_generation INTEGER DEFAULT 0,
            version TEXT DEFAULT '1.0',
            script_metadata TEXT
        )''',
        
        '''CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            resource_id TEXT NOT NULL,
            timestamp REAL NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            request_id TEXT,
            details TEXT,
            status TEXT DEFAULT 'success'
        )''',
        
        '''CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            user_id TEXT REFERENCES "user"(user_id),
            content_id TEXT REFERENCES content(content_id),
            event_data TEXT,
            timestamp REAL NOT NULL,
            ip_address TEXT
        )''',
        
        '''CREATE TABLE IF NOT EXISTS system_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            module TEXT,
            timestamp REAL NOT NULL,
            user_id TEXT REFERENCES "user"(user_id),
            extra_data TEXT,
            error_details TEXT,
            traceback TEXT
        )''',
        
        '''CREATE TABLE IF NOT EXISTS invitations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            inviter_id TEXT REFERENCES "user"(user_id),
            invitation_token TEXT UNIQUE NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            used INTEGER DEFAULT 0,
            used_at REAL
        )'''
    ]
    
    for i, table_sql in enumerate(tables, 1):
        try:
            cur.execute(table_sql)
            print(f"[OK] Table {i}/8 created/verified")
        except Exception as e:
            print(f"[ERROR] Table {i}/8 failed: {e}")
    
    conn.commit()
    conn.close()
    print(f"\n[SUCCESS] SQLite database initialized successfully at {db_path}!")

def main():
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print(f"\nDatabase URL: {DATABASE_URL[:50]}...")
    
    if "postgresql" in DATABASE_URL:
        print("\nInitializing PostgreSQL database...")
        init_postgresql()
    else:
        print("\nInitializing SQLite database...")
        init_sqlite()
    
    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print("\nYou can now:")
    print("1. Start the server: python scripts/start_server.py")
    print("2. Register a user: curl -X POST http://localhost:9000/users/register \\")
    print('   -H "Content-Type: application/json" \\')
    print('   -d \'{"username": "admin", "email": "admin@example.com", "password": "admin123"}\'')
    print("3. Test endpoints: http://localhost:9000/docs")

if __name__ == "__main__":
    main()
