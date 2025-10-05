#!/usr/bin/env python3
"""
Setup Correct Supabase Connection
Using your exact credentials and region
"""

import os

def setup_supabase():
    print("🔧 Setting up Supabase with correct credentials")
    print("=" * 50)
    
    # Your exact working connection string
    DATABASE_URL = "postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres"
    
    # Test connection first
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()[0]
        cur.close()
        conn.close()
        print(f"✅ Connection successful! PostgreSQL: {version[:50]}...")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Create .env with all your credentials
    env_content = f"""# Database Configuration - Supabase Primary
DATABASE_URL={DATABASE_URL}

# Supabase Configuration
SUPABASE_URL=https://dusqpdhojbgfxwflukhc.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR1c3FwZGhvamJnZnh3Zmx1a2hjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyMDcwNTIsImV4cCI6MjA3Mzc4MzA1Mn0.Is0lvgpi1Ijc3jZ8-DQmnrRPqiFfnrQblXzmVKQqY4c
SUPABASE_DB_PASSWORD=Moto%40Roxy123

# Authentication & Security
JWT_SECRET_KEY=SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==
JWS_SECRET=SJOYupb2v8rFU8nd3+B7G/5Y90BB+x0ihG+vTZ6M3lcAKnC0ThJtBEQvZz5ZgigQ+ZC96vAbmJQ0+1FMtLmqUw==
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Observability & Monitoring
SENTRY_DSN=https://0d595f5827bf2a4ae5da7d1ed1a09338@o4509949438328832.ingest.us.sentry.io/4510035576946688
POSTHOG_API_KEY=phc_lmGvuDZ7JiyjDmkL1T6Wy3TvDHgFdjt1zlH02fVziwU
POSTHOG_HOST=https://us.posthog.com
ENVIRONMENT=development

# Storage Configuration
USE_S3_STORAGE=false
USE_SUPABASE_STORAGE=true
BHIV_STORAGE_BACKEND=supabase

# Supabase Storage
SUPABASE_BUCKET_NAME=ai-agent-files

# Local Storage Fallback
BHIV_BUCKET_PATH=bucket

# Rate Limiting & Performance
REDIS_URL=redis://localhost:6379
MAX_UPLOAD_SIZE_MB=100
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# GDPR & Privacy
DATA_RETENTION_DAYS=365
AUTO_DELETE_EXPIRED_DATA=true
GDPR_CONTACT_EMAIL=privacy@yourcompany.com

# Additional APIs
PERPLEXITY_API_KEY=your-perplexity-key
BHIV_LM_URL=http://localhost:8001
BHIV_LM_API_KEY=demo_api_key_123
"""
    
    # Write .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created with correct credentials")
    
    # Create Supabase tables
    try:
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Supabase tables created successfully!")
    except Exception as e:
        print(f"⚠️  Table creation: {e}")
    
    # Create demo user in Supabase
    try:
        import psycopg2
        import time
        from passlib.context import CryptContext
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Create demo user
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        demo_hash = pwd_context.hash("demo1234")
        
        cur.execute("""
            INSERT INTO "user" (user_id, username, password_hash, email, email_verified, created_at, role)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET
                password_hash = EXCLUDED.password_hash
        """, (
            'demo001', 'demo', demo_hash, 'demo@example.com', 
            True, time.time(), 'user'
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Demo user created in Supabase (username: demo, password: demo1234)")
        
    except Exception as e:
        print(f"⚠️  Demo user creation: {e}")
    
    print(f"\n🎉 Supabase setup complete!")
    print(f"📊 Project: dusqpdhojbgfxwflukhc (ap-south-1)")
    print(f"🔗 Database: PostgreSQL (Supabase)")
    print(f"🚀 Ready to start server!")
    
    return True

if __name__ == "__main__":
    setup_supabase()