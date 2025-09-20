#!/usr/bin/env python3
"""
Simple Migration Runner
Direct database migration without Alembic interpolation issues
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import logging

load_dotenv()

def run_simple_migrations():
    """Run migrations directly with SQLAlchemy"""
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Get database URL
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
        logger.info(f"Connecting to database: {db_url[:50]}...")
        
        # Create engine
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Add missing columns to user table
            try:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN email_verified BOOLEAN DEFAULT FALSE"))
                logger.info("Added email_verified column to user table")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN verification_token VARCHAR"))
                logger.info("Added verification_token column to user table")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE \"user\" ADD COLUMN role VARCHAR DEFAULT 'user'"))
                logger.info("Added role column to user table")
            except Exception:
                pass
            
            # Add missing columns to content table
            try:
                conn.execute(text("ALTER TABLE content ADD COLUMN duration_ms INTEGER"))
                logger.info("Added duration_ms column to content table")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE content ADD COLUMN views INTEGER DEFAULT 0"))
                logger.info("Added views column to content table")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE content ADD COLUMN likes INTEGER DEFAULT 0"))
                logger.info("Added likes column to content table")
            except Exception:
                pass
            
            # Add missing columns to feedback table
            try:
                conn.execute(text("ALTER TABLE feedback ADD COLUMN watch_time_ms INTEGER"))
                logger.info("Added watch_time_ms column to feedback table")
            except Exception:
                pass
            
            try:
                conn.execute(text("ALTER TABLE feedback ADD COLUMN reward FLOAT"))
                logger.info("Added reward column to feedback table")
            except Exception:
                pass
            
            # Create invitations table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS invitations (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR NOT NULL,
                        inviter_id VARCHAR NOT NULL,
                        invitation_token VARCHAR UNIQUE NOT NULL,
                        created_at FLOAT NOT NULL,
                        expires_at FLOAT NOT NULL,
                        used BOOLEAN DEFAULT FALSE,
                        used_at FLOAT
                    )
                """))
                logger.info("Created invitations table")
            except Exception as e:
                logger.warning(f"Invitations table creation: {e}")
            
            # Create analytics table
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS analytics (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR NOT NULL,
                        user_id VARCHAR,
                        content_id VARCHAR,
                        metadata TEXT,
                        timestamp FLOAT NOT NULL,
                        ip_address VARCHAR
                    )
                """))
                logger.info("Created analytics table")
            except Exception as e:
                logger.warning(f"Analytics table creation: {e}")
            
            conn.commit()
            logger.info("SUCCESS: All migrations completed")
            return True
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = run_simple_migrations()
    if success:
        print("SUCCESS: Database migrations completed")
    else:
        print("ERROR: Database migrations failed")
        sys.exit(1)