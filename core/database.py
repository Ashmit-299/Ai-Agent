import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix psycopg2 import issue
try:
    import psycopg2
except ImportError:
    try:
        import psycopg2_binary as psycopg2
        import sys
        sys.modules['psycopg2'] = psycopg2
    except ImportError:
        pass

from sqlmodel import SQLModel, create_engine, Session, select
from .models import User, Content, Feedback, Script
from typing import Optional, List
import json
import time
from datetime import datetime

# Use Supabase PostgreSQL for production, SQLite for fallback
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_agent.db")

# Add analytics and logs functions
class DatabaseManager:
    @staticmethod
    def save_analytics(event_type: str, user_id: str = None, content_id: str = None, event_data: dict = None, ip_address: str = None):
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import json
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO analytics (event_type, user_id, content_id, event_data, timestamp, ip_address)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    event_type, user_id, content_id, 
                    json.dumps(event_data) if event_data else None,
                    time.time(), ip_address
                ))
                conn.commit()
                cur.close()
                conn.close()
                print("Analytics saved to Supabase")
                return True
            except Exception as e:
                print(f"Supabase analytics failed: {e}")
                return False
        return False
    
    @staticmethod
    def save_system_log(level: str, message: str, module: str = None, user_id: str = None):
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO system_logs (level, message, module, timestamp, user_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (level, message, module, time.time(), user_id))
                conn.commit()
                cur.close()
                conn.close()
                print("System log saved to Supabase")
                return True
            except Exception as e:
                print(f"Supabase system log failed: {e}")
                return False
        return False
print(f"Using database: {'PostgreSQL (Supabase)' if 'postgresql' in DATABASE_URL else 'SQLite'}")

# Engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_size=5,
        max_overflow=10
    )

def create_db_and_tables():
    try:
        SQLModel.metadata.create_all(engine)
    except Exception as e:
        print(f"Table creation failed: {e}")
        pass  # Tables may already exist

def get_session():
    with Session(engine) as session:
        yield session

class DatabaseManager:
    def __init__(self, db_path=None):
        if db_path:
            self.engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
        else:
            self.engine = engine
    
    def get_connection(self):
        return self.engine.connect()
    
    @staticmethod
    def create_user(user_data: dict):
        try:
            with Session(engine) as session:
                user = User(**user_data)
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        except Exception as e:
            print(f"Database user creation failed: {e}")
            # Fallback to SQLite for development
            try:
                import sqlite3
                import time
                conn = sqlite3.connect('data.db')
                with conn:
                    cur = conn.cursor()
                    cur.execute('''
                        CREATE TABLE IF NOT EXISTS user (
                            user_id TEXT PRIMARY KEY,
                            username TEXT UNIQUE,
                            password_hash TEXT,
                            email TEXT,
                            email_verified BOOLEAN DEFAULT FALSE,
                            verification_token TEXT,
                            sub TEXT,
                            role TEXT DEFAULT 'user',
                            last_login REAL,
                            created_at REAL
                        )
                    ''')
                    cur.execute('''
                        INSERT INTO user (user_id, username, password_hash, email, email_verified, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        user_data['user_id'],
                        user_data['username'], 
                        user_data['password_hash'],
                        user_data['email'],
                        user_data.get('email_verified', False),
                        user_data.get('created_at', time.time())
                    ))
                conn.close()
                print(f"User created in SQLite fallback: {user_data['username']}")
            except Exception as sqlite_error:
                print(f"SQLite fallback also failed: {sqlite_error}")
            
            # Return a mock user object
            class MockUser:
                def __init__(self, **kwargs):
                    for k, v in kwargs.items():
                        setattr(self, k, v)
            
            return MockUser(**user_data)
    
    @staticmethod
    def get_user_by_username(username: str):
        try:
            with Session(engine) as session:
                statement = select(User).where(User.username == username)
                user = session.exec(statement).first()
                if user:
                    return user
        except Exception as e:
            print(f"SQLModel user query failed: {e}")
        
        # Fallback to SQLite database
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                cur.execute('SELECT user_id, username, password_hash, email, email_verified, created_at FROM user WHERE username=?', (username,))
                row = cur.fetchone()
            conn.close()
            
            if row:
                class MockUser:
                    def __init__(self, user_id, username, password_hash, email, email_verified, created_at):
                        self.user_id = user_id
                        self.username = username
                        self.password_hash = password_hash
                        self.email = email
                        self.email_verified = email_verified
                        self.created_at = created_at
                
                return MockUser(*row)
        except Exception as sqlite_error:
            print(f"SQLite fallback also failed: {sqlite_error}")
        
        return None
    
    @staticmethod
    def get_user_by_id(user_id: str):
        try:
            with Session(engine) as session:
                statement = select(User).where(User.user_id == user_id)
                user = session.exec(statement).first()
                if user:
                    return user
        except Exception as e:
            print(f"SQLModel user query failed: {e}")
        
        # Fallback to SQLite database
        try:
            import sqlite3
            conn = sqlite3.connect('data.db')
            with conn:
                cur = conn.cursor()
                cur.execute('SELECT user_id, username, password_hash, email, email_verified, created_at FROM user WHERE user_id=?', (user_id,))
                row = cur.fetchone()
            conn.close()
            
            if row:
                class MockUser:
                    def __init__(self, user_id, username, password_hash, email, email_verified, created_at):
                        self.user_id = user_id
                        self.username = username
                        self.password_hash = password_hash
                        self.email = email
                        self.email_verified = email_verified
                        self.created_at = created_at
                
                return MockUser(*row)
        except Exception as sqlite_error:
            print(f"SQLite fallback also failed: {sqlite_error}")
        
        return None
    
    @staticmethod
    def create_content(content_data: dict):
        with Session(engine) as session:
            content = Content(**content_data)
            session.add(content)
            session.commit()
            session.refresh(content)
            return content
    
    @staticmethod
    def get_content_by_id(content_id: str):
        with Session(engine) as session:
            statement = select(Content).where(Content.content_id == content_id)
            return session.exec(statement).first()
    
    @staticmethod
    def create_feedback(feedback_data: dict):
        # Use raw SQL for Supabase
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    feedback_data['content_id'],
                    feedback_data['user_id'], 
                    feedback_data['event_type'],
                    feedback_data.get('watch_time_ms', 0),
                    feedback_data['reward'],
                    feedback_data['rating'],
                    feedback_data['comment'],
                    feedback_data['timestamp']
                ))
                conn.commit()
                cur.close()
                conn.close()
                print("Feedback saved to Supabase")
                return True
            except Exception as e:
                print(f"Supabase feedback failed: {e}")
                raise e
        else:
            # SQLite fallback
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                with conn:
                    cur = conn.cursor()
                    cur.execute('''
                        INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        feedback_data['content_id'],
                        feedback_data['user_id'],
                        feedback_data['event_type'],
                        feedback_data.get('watch_time_ms', 0),
                        feedback_data['reward'],
                        feedback_data['rating'],
                        feedback_data['comment'],
                        feedback_data['timestamp']
                    ))
                conn.close()
                return True
            except Exception as sqlite_error:
                raise sqlite_error
    
    @staticmethod
    def create_script(script_data: dict):
        # Use raw SQL for Supabase
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    script_data['script_id'],
                    script_data.get('content_id'),
                    script_data['user_id'],
                    script_data['title'],
                    script_data['script_content'],
                    script_data.get('script_type', 'text'),
                    script_data.get('file_path'),
                    script_data['created_at'],
                    script_data.get('used_for_generation', False)
                ))
                conn.commit()
                cur.close()
                conn.close()
                print("Script saved to Supabase")
                return True
            except Exception as e:
                print(f"Supabase script failed: {e}")
                return None
        else:
            return None
    
    @staticmethod
    def get_script_by_id(script_id: str):
        try:
            with Session(engine) as session:
                statement = select(Script).where(Script.script_id == script_id)
                return session.exec(statement).first()
        except Exception as e:
            print(f"Script query failed (table may not exist): {e}")
            return None
    
    @staticmethod
    def get_analytics_data() -> dict:
        # Use raw SQL queries to avoid SQLModel column issues
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Get user count
                cur.execute('SELECT COUNT(*) FROM "user"')
                total_users = cur.fetchone()[0]
                
                # Get content count
                cur.execute('SELECT COUNT(*) FROM content')
                total_content = cur.fetchone()[0]
                
                # Get feedback count
                cur.execute('SELECT COUNT(*) FROM feedback')
                total_feedback = cur.fetchone()[0]
                
                # Get scripts count (handle if table doesn't exist)
                try:
                    cur.execute('SELECT COUNT(*) FROM script')
                    total_scripts = cur.fetchone()[0]
                except Exception:
                    total_scripts = 0
                
                # Get average rating
                cur.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
                avg_rating = cur.fetchone()[0] or 0.0
                
                # Get sentiment breakdown (handle if column doesn't exist)
                sentiment_counts = {}
                try:
                    cur.execute('SELECT sentiment, COUNT(*) FROM feedback WHERE sentiment IS NOT NULL GROUP BY sentiment')
                    sentiment_counts = dict(cur.fetchall())
                except Exception:
                    sentiment_counts = {}
                
                # Get average engagement (handle if column doesn't exist)
                avg_engagement = 0.0
                try:
                    cur.execute('SELECT AVG(engagement_score) FROM feedback WHERE engagement_score IS NOT NULL')
                    avg_engagement = cur.fetchone()[0] or 0.0
                except Exception:
                    avg_engagement = 0.0
                
                cur.close()
                conn.close()
                
                return {
                    "total_users": total_users,
                    "total_content": total_content,
                    "total_feedback": total_feedback,
                    "total_scripts": total_scripts,
                    "average_rating": round(avg_rating, 2),
                    "average_engagement": round(avg_engagement, 2),
                    "sentiment_breakdown": sentiment_counts
                }
            except Exception as e:
                print(f"PostgreSQL analytics query failed: {e}")
                return {
                    "total_users": 0,
                    "total_content": 0,
                    "total_feedback": 0,
                    "total_scripts": 0,
                    "average_rating": 0.0,
                    "average_engagement": 0.0,
                    "sentiment_breakdown": {},
                    "error": str(e)
                }
        else:
            # SQLite fallback
            try:
                import sqlite3
                conn = sqlite3.connect('data.db')
                cur = conn.cursor()
                
                cur.execute('SELECT COUNT(*) FROM user')
                total_users = cur.fetchone()[0]
                
                cur.execute('SELECT COUNT(*) FROM content')
                total_content = cur.fetchone()[0]
                
                cur.execute('SELECT COUNT(*) FROM feedback')
                total_feedback = cur.fetchone()[0]
                
                cur.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
                avg_rating = cur.fetchone()[0] or 0.0
                
                conn.close()
                
                return {
                    "total_users": total_users,
                    "total_content": total_content,
                    "total_feedback": total_feedback,
                    "total_scripts": 0,
                    "average_rating": round(avg_rating, 2),
                    "average_engagement": 0.0,
                    "sentiment_breakdown": {}
                }
            except Exception as e:
                return {
                    "total_users": 0,
                    "total_content": 0,
                    "total_feedback": 0,
                    "total_scripts": 0,
                    "average_rating": 0.0,
                    "average_engagement": 0.0,
                    "sentiment_breakdown": {},
                    "error": str(e)
                }

# Initialize database
create_db_and_tables()
db = DatabaseManager()