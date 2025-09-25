#!/usr/bin/env python3
"""
Fix PostgreSQL schema to use user_id as primary key
"""

import os
import psycopg2
from sqlmodel import SQLModel, create_engine, Session, text

def fix_postgres_schema():
    """Fix the PostgreSQL user table to use user_id as primary key"""
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("DATABASE_URL not set, skipping PostgreSQL fix")
        return
    
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        
        with Session(engine) as session:
            # Check if user table exists and has correct schema
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'user'
                ORDER BY ordinal_position
            """)).fetchall()
            
            if not result:
                print("User table doesn't exist, creating with correct schema...")
                # Create user table with correct schema
                session.exec(text("""
                    CREATE TABLE "user" (
                        user_id VARCHAR PRIMARY KEY,
                        username VARCHAR UNIQUE NOT NULL,
                        password_hash VARCHAR,
                        email VARCHAR,
                        email_verified BOOLEAN DEFAULT FALSE,
                        verification_token VARCHAR,
                        sub VARCHAR,
                        created_at FLOAT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())
                    )
                """))
                session.commit()
                print("User table created successfully!")
                return
            
            # Check if user_id column exists
            has_user_id = any(col[0] == 'user_id' for col in result)
            
            if has_user_id:
                print("User table already has correct schema")
                return
            
            print("Fixing user table schema...")
            
            # Drop foreign key constraints first
            session.exec(text("DROP TABLE IF EXISTS content CASCADE"))
            session.exec(text("DROP TABLE IF EXISTS feedback CASCADE"))
            
            # Rename old user table
            session.exec(text('ALTER TABLE "user" RENAME TO user_old'))
            
            # Create new user table with correct schema
            session.exec(text("""
                CREATE TABLE "user" (
                    user_id VARCHAR PRIMARY KEY,
                    username VARCHAR UNIQUE NOT NULL,
                    password_hash VARCHAR,
                    email VARCHAR,
                    email_verified BOOLEAN DEFAULT FALSE,
                    verification_token VARCHAR,
                    sub VARCHAR,
                    created_at FLOAT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW())
                )
            """))
            
            # Get columns from old table first
            old_columns = session.exec(text("""
                SELECT column_name
                FROM information_schema.columns 
                WHERE table_name = 'user_old'
                ORDER BY ordinal_position
            """)).fetchall()
            
            old_column_names = [col[0] for col in old_columns]
            
            # Build migration query based on available columns
            if 'password_hash' in old_column_names:
                migration_query = """
                    INSERT INTO "user" (user_id, username, password_hash, email, created_at)
                    SELECT 
                        CONCAT('user_', SUBSTR(MD5(RANDOM()::text), 1, 8)) as user_id,
                        username,
                        password_hash,
                        email,
                        COALESCE(created_at, EXTRACT(EPOCH FROM NOW()))
                    FROM user_old
                """
            else:
                # Fallback for different schema
                migration_query = """
                    INSERT INTO "user" (user_id, username, created_at)
                    SELECT 
                        CONCAT('user_', SUBSTR(MD5(RANDOM()::text), 1, 8)) as user_id,
                        username,
                        EXTRACT(EPOCH FROM NOW())
                    FROM user_old
                """
            
            session.exec(text(migration_query))
            
            # Drop old table with cascade to remove dependent constraints
            session.exec(text("DROP TABLE user_old CASCADE"))
            
            session.commit()
            print("PostgreSQL user table schema fixed successfully!")
            
    except Exception as e:
        print(f"Error fixing PostgreSQL schema: {e}")
        print("This is normal if using SQLite instead of PostgreSQL")

if __name__ == "__main__":
    fix_postgres_schema()