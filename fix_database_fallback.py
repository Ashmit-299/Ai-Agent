#!/usr/bin/env python3
"""
Fix Database Fallback - Switch to SQLite and create demo user
"""

import os
import sqlite3
import time
from passlib.context import CryptContext

def fix_database():
    print("🔧 Fixing Database Configuration")
    print("=" * 40)
    
    # Update .env to use SQLite
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Comment out problematic DATABASE_URL
    lines = env_content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith("DATABASE_URL=postgresql://"):
            lines[i] = f"# {line}"
            lines.insert(i+1, "DATABASE_URL=sqlite:///./ai_agent.db")
            break
    
    env_content = '\n'.join(lines)
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Switched to SQLite database")
    
    # Create SQLite database and tables
    conn = sqlite3.connect('ai_agent.db')
    with conn:
        cur = conn.cursor()
        
        # Create user table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                email_verified BOOLEAN DEFAULT FALSE,
                created_at REAL,
                verification_token TEXT,
                sub TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        
        # Create content table
        cur.execute('''
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
        ''')
        
        # Create feedback table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT,
                user_id TEXT,
                event_type TEXT,
                watch_time_ms INTEGER,
                reward REAL,
                rating INTEGER,
                comment TEXT,
                timestamp REAL,
                sentiment TEXT,
                engagement_score REAL,
                ip_address TEXT
            )
        ''')
        
        # Create demo user
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        demo_hash = pwd_context.hash("demo1234")
        
        cur.execute('''
            INSERT OR REPLACE INTO user 
            (user_id, username, password_hash, email, email_verified, created_at, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            'demo001', 'demo', demo_hash, 'demo@example.com', 
            True, time.time(), 'user'
        ))
        
        print("✅ Database tables created")
        print("✅ Demo user created (username: demo, password: demo1234)")
    
    conn.close()
    return True

if __name__ == "__main__":
    fix_database()