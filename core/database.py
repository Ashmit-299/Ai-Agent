import os
from dotenv import load_dotenv

# Load environment variables - v1.0.1 metrics fix
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
from .models import User, Content, Feedback, Script, AuditLog
from typing import Optional, List
import json
import time
from datetime import datetime

# Prioritize Supabase PostgreSQL, fallback to SQLite only if Supabase not configured
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Check for explicit DATABASE_URL first
DATABASE_URL = os.getenv("DATABASE_URL")

# If no explicit DATABASE_URL, try to build from Supabase credentials
if not DATABASE_URL or DATABASE_URL == "sqlite:///./ai_agent.db":
    if SUPABASE_URL and SUPABASE_ANON_KEY and SUPABASE_URL != "https://your-project.supabase.co":
        # Extract project ID from Supabase URL
        import re
        match = re.search(r'https://([^.]+)\.supabase\.co', SUPABASE_URL)
        if match:
            project_id = match.group(1)
            SUPABASE_DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD")
            if SUPABASE_DB_PASSWORD:
                DATABASE_URL = f"postgresql://postgres.{project_id}:{SUPABASE_DB_PASSWORD}@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
                print(f"SUCCESS: Using Supabase PostgreSQL: {project_id}")
            else:
                print("INFO: No SUPABASE_DB_PASSWORD found, using SQLite")
                DATABASE_URL = "sqlite:///./ai_agent.db"
        else:
            print(f"ERROR: Invalid Supabase URL format: {SUPABASE_URL}")
            DATABASE_URL = "sqlite:///./ai_agent.db"
    else:
        DATABASE_URL = "sqlite:///./ai_agent.db"

# Final fallback
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./ai_agent.db"

# Add analytics and logs functions
class DatabaseManager:
    @staticmethod
    def save_analytics(event_type: str, user_id: str = None, content_id: str = None, event_data: dict = None, ip_address: str = None):
        """Save analytics data to Supabase"""
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
                print(f"✅ Analytics saved to Supabase: {event_type}")
                return True
            except Exception as e:
                print(f"❌ Supabase analytics failed: {e}")
                return False
        return False
    
    @staticmethod
    def save_system_log(level: str, message: str, module: str = None, user_id: str = None, error_details: str = None, traceback: str = None):
        """Save system logs to Supabase"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO system_logs (level, message, module, timestamp, user_id, error_details, traceback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (level, message, module, time.time(), user_id, error_details, traceback))
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ System log saved to Supabase: {level} - {message[:50]}...")
                return True
            except Exception as e:
                print(f"❌ Supabase system log failed: {e}")
                return False
        return False
# Database status reporting
if 'postgresql' in DATABASE_URL:
    print("SUCCESS: Using database: PostgreSQL (Supabase)")
    print(f"Connection: {DATABASE_URL[:50]}...")
else:
    print("WARNING: Using database: SQLite (fallback)")
    print("INFO: To use Supabase: Run 'python setup_supabase.py' to configure")
    print(f"SQLite file: {DATABASE_URL}")

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
        if 'postgresql' in DATABASE_URL:
            print("SUCCESS: Supabase tables created/verified successfully!")
        else:
            print("SUCCESS: SQLite tables created/verified successfully!")
    except Exception as e:
        print(f"ERROR: Table creation failed: {e}")
        if 'postgresql' in DATABASE_URL:
            print("INFO: Check your Supabase credentials and network connection")
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
        """Create user in Supabase with proper error handling"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO "user" (user_id, username, password_hash, email, email_verified, verification_token, sub, role, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        password_hash = EXCLUDED.password_hash,
                        email = EXCLUDED.email
                    RETURNING user_id, username, email
                """, (
                    user_data['user_id'],
                    user_data['username'],
                    user_data['password_hash'],
                    user_data.get('email'),
                    user_data.get('email_verified', False),
                    user_data.get('verification_token'),
                    user_data.get('sub'),
                    user_data.get('role', 'user'),
                    user_data.get('created_at', time.time())
                ))
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ User created in Supabase: {user_data['username']}")
                
                # Return user-like object
                class SupabaseUser:
                    def __init__(self, **kwargs):
                        for k, v in kwargs.items():
                            setattr(self, k, v)
                
                return SupabaseUser(**user_data)
            except Exception as e:
                print(f"❌ Supabase user creation failed: {e}")
                raise e
        else:
            # SQLModel fallback
            try:
                with Session(engine) as session:
                    user = User(**user_data)
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    return user
            except Exception as e:
                print(f"❌ SQLModel user creation failed: {e}")
                raise e
    
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
        """Create content in Supabase with proper error handling"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (content_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        description = EXCLUDED.description,
                        views = content.views + 1
                    RETURNING content_id, title
                """, (
                    content_data['content_id'],
                    content_data['uploader_id'],
                    content_data['title'],
                    content_data.get('description'),
                    content_data['file_path'],
                    content_data['content_type'],
                    content_data.get('duration_ms', 0),
                    content_data.get('uploaded_at', time.time()),
                    content_data.get('authenticity_score', 0.0),
                    content_data.get('current_tags'),
                    content_data.get('views', 0),
                    content_data.get('likes', 0),
                    content_data.get('shares', 0)
                ))
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ Content saved to Supabase: {content_data['content_id']}")
                
                # Return content-like object
                class SupabaseContent:
                    def __init__(self, **kwargs):
                        for k, v in kwargs.items():
                            setattr(self, k, v)
                
                return SupabaseContent(**content_data)
            except Exception as e:
                print(f"❌ Supabase content creation failed: {e}")
                raise e
        else:
            # SQLModel fallback
            try:
                with Session(engine) as session:
                    content = Content(**content_data)
                    session.add(content)
                    session.commit()
                    session.refresh(content)
                    return content
            except Exception as e:
                print(f"❌ SQLModel content creation failed: {e}")
                raise e
    
    @staticmethod
    def get_content_by_id(content_id: str):
        with Session(engine) as session:
            statement = select(Content).where(Content.content_id == content_id)
            return session.exec(statement).first()
    
    @staticmethod
    def get_recent_content(limit: int = 20):
        try:
            with Session(engine) as session:
                statement = select(Content).order_by(Content.uploaded_at.desc()).limit(limit)
                return session.exec(statement).all()
        except Exception as e:
            print(f"SQLModel content query failed: {e}")
            return []
    
    @staticmethod
    def create_feedback(feedback_data: dict):
        """Create feedback in Supabase with enhanced data capture"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO feedback (content_id, user_id, event_type, watch_time_ms, reward, rating, comment, sentiment, engagement_score, ip_address, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    feedback_data['content_id'],
                    feedback_data['user_id'], 
                    feedback_data['event_type'],
                    feedback_data.get('watch_time_ms', 0),
                    feedback_data.get('reward', 0.0),
                    feedback_data.get('rating'),
                    feedback_data.get('comment'),
                    feedback_data.get('sentiment'),
                    feedback_data.get('engagement_score'),
                    feedback_data.get('ip_address'),
                    feedback_data.get('timestamp', time.time())
                ))
                feedback_id = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ Feedback saved to Supabase: ID {feedback_id}")
                return feedback_id
            except Exception as e:
                print(f"❌ Supabase feedback failed: {e}")
                raise e
        else:
            # SQLModel fallback
            try:
                with Session(engine) as session:
                    feedback = Feedback(**feedback_data)
                    session.add(feedback)
                    session.commit()
                    session.refresh(feedback)
                    return feedback.id
            except Exception as e:
                print(f"❌ SQLModel feedback creation failed: {e}")
                raise e
    
    @staticmethod
    def create_script(script_data: dict):
        """Create script in Supabase with enhanced metadata"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                import time
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation, version, script_metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (script_id) DO UPDATE SET
                        title = EXCLUDED.title,
                        script_content = EXCLUDED.script_content,
                        used_for_generation = EXCLUDED.used_for_generation
                    RETURNING script_id
                """, (
                    script_data['script_id'],
                    script_data.get('content_id'),
                    script_data['user_id'],
                    script_data['title'],
                    script_data['script_content'],
                    script_data.get('script_type', 'text'),
                    script_data.get('file_path'),
                    script_data.get('created_at', time.time()),
                    script_data.get('used_for_generation', False),
                    script_data.get('version', '1.0'),
                    script_data.get('script_metadata')
                ))
                result = cur.fetchone()
                conn.commit()
                cur.close()
                conn.close()
                print(f"✅ Script saved to Supabase: {script_data['script_id']}")
                return result[0] if result else script_data['script_id']
            except Exception as e:
                print(f"❌ Supabase script failed: {e}")
                raise e
        else:
            # SQLModel fallback
            try:
                with Session(engine) as session:
                    script = Script(**script_data)
                    session.add(script)
                    session.commit()
                    session.refresh(script)
                    return script.script_id
            except Exception as e:
                print(f"❌ SQLModel script creation failed: {e}")
                raise e
    
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
    def create_audit_log(audit_data: dict):
        """Create audit log entry"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO audit_logs (user_id, action, resource_type, resource_id, timestamp, ip_address, user_agent, request_id, details, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    audit_data.get('user_id'),
                    audit_data['action'],
                    audit_data['resource_type'],
                    audit_data['resource_id'],
                    audit_data.get('timestamp', time.time()),
                    audit_data.get('ip_address'),
                    audit_data.get('user_agent'),
                    audit_data.get('request_id'),
                    audit_data.get('details'),
                    audit_data.get('status', 'success')
                ))
                conn.commit()
                cur.close()
                conn.close()
                return True
            except Exception as e:
                print(f"Audit log creation failed: {e}")
                return False
        return False
    
    @staticmethod
    def delete_user_data(user_id: str):
        """GDPR: Delete all user data"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Delete in order to respect foreign key constraints
                cur.execute('DELETE FROM feedback WHERE user_id = %s', (user_id,))
                cur.execute('DELETE FROM script WHERE user_id = %s', (user_id,))
                cur.execute('DELETE FROM content WHERE uploader_id = %s', (user_id,))
                cur.execute('DELETE FROM "user" WHERE user_id = %s', (user_id,))
                
                conn.commit()
                cur.close()
                conn.close()
                return True
            except Exception as e:
                print(f"User data deletion failed: {e}")
                return False
        return False
    
    @staticmethod
    def export_user_data(user_id: str):
        """GDPR: Export all user data"""
        if 'postgresql' in DATABASE_URL:
            try:
                import psycopg2
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Get user data
                cur.execute('SELECT * FROM "user" WHERE user_id = %s', (user_id,))
                user_data = cur.fetchone()
                
                # Get content data
                cur.execute('SELECT * FROM content WHERE uploader_id = %s', (user_id,))
                content_data = cur.fetchall()
                
                # Get feedback data
                cur.execute('SELECT * FROM feedback WHERE user_id = %s', (user_id,))
                feedback_data = cur.fetchall()
                
                # Get script data
                cur.execute('SELECT * FROM script WHERE user_id = %s', (user_id,))
                script_data = cur.fetchall()
                
                cur.close()
                conn.close()
                
                return {
                    'user': user_data,
                    'content': content_data,
                    'feedback': feedback_data,
                    'scripts': script_data
                }
            except Exception as e:
                print(f"User data export failed: {e}")
                return {}
        return {}
    
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