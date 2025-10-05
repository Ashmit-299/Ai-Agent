#!/usr/bin/env python3
"""
Supabase Setup Script for AI Agent
Configures Supabase as primary database with SQLite fallback
"""

import os
import sys
from dotenv import load_dotenv

def setup_supabase():
    """Interactive Supabase setup"""
    print("🚀 AI Agent - Supabase Database Setup")
    print("=" * 50)
    
    # Load existing .env if it exists
    if os.path.exists('.env'):
        load_dotenv()
        print("✅ Found existing .env file")
    else:
        print("📝 Creating new .env file from template")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
        else:
            with open('.env', 'w') as f:
                f.write("# AI Agent Environment Configuration\n")
    
    print("\n📋 Supabase Configuration Required:")
    print("1. Go to https://supabase.com and create a new project")
    print("2. Get your project URL and anon key from Settings > API")
    print("3. Get your database password from Settings > Database")
    
    # Get Supabase credentials
    supabase_url = input("\n🔗 Enter your Supabase URL (https://your-project.supabase.co): ").strip()
    if not supabase_url.startswith('https://'):
        print("❌ Invalid URL format. Must start with https://")
        return False
    
    supabase_key = input("🔑 Enter your Supabase anon key: ").strip()
    if len(supabase_key) < 50:
        print("❌ Anon key seems too short. Please check and try again.")
        return False
    
    db_password = input("🔐 Enter your Supabase database password: ").strip()
    if len(db_password) < 8:
        print("❌ Database password seems too short. Please check and try again.")
        return False
    
    # Extract project ID from URL
    import re
    match = re.search(r'https://([^.]+)\.supabase\.co', supabase_url)
    if not match:
        print("❌ Could not extract project ID from URL")
        return False
    
    project_id = match.group(1)
    # Try different connection formats
    connection_formats = [
        f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres",
        f"postgresql://postgres.{project_id}:{db_password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        f"postgresql://postgres:{db_password}@aws-0-us-east-1.pooler.supabase.com:5432/postgres?host=db.{project_id}.supabase.co"
    ]
    
    database_url = None
    for url_format in connection_formats:
        try:
            import psycopg2
            test_conn = psycopg2.connect(url_format)
            test_conn.close()
            database_url = url_format
            print(f"✅ Connection successful with format: {url_format[:60]}...")
            break
        except Exception as e:
            print(f"❌ Failed format {url_format[:60]}...: {str(e)[:50]}...")
            continue
    
    if not database_url:
        print("❌ All connection formats failed. Using direct connection format.")
        database_url = f"postgresql://postgres:{db_password}@db.{project_id}.supabase.co:5432/postgres"
    
    # Update .env file
    env_vars = {
        'DATABASE_URL': database_url,
        'SUPABASE_URL': supabase_url,
        'SUPABASE_ANON_KEY': supabase_key,
        'SUPABASE_DB_PASSWORD': db_password,
        'USE_SUPABASE_STORAGE': 'true',
        'BHIV_STORAGE_BACKEND': 'supabase'
    }
    
    # Read existing .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update or add variables
    for key, value in env_vars.items():
        if f"{key}=" in env_content:
            # Update existing
            lines = env_content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith(f"{key}="):
                    lines[i] = f"{key}={value}"
            env_content = '\n'.join(lines)
        else:
            # Add new
            env_content += f"\n{key}={value}"
    
    # Write updated .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ Supabase configuration saved to .env")
    print(f"📊 Project ID: {project_id}")
    print(f"🔗 Database URL: {database_url[:50]}...")
    
    # Test connection (already tested above if database_url was found)
    print("\n🧪 Final connection test...")
    try:
        if database_url:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            cur.close()
            conn.close()
            print(f"✅ Final test successful! PostgreSQL version: {version[:50]}...")
        else:
            raise Exception("No valid database URL found")
        
        # Create tables
        print("\n📋 Creating database tables...")
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Database tables created successfully!")
        
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Check your credentials and try again")
        return False

def test_configuration():
    """Test current configuration"""
    print("\n🧪 Testing Current Configuration")
    print("=" * 40)
    
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL')
    supabase_url = os.getenv('SUPABASE_URL')
    
    if not database_url:
        print("❌ No DATABASE_URL found in .env")
        return False
    
    if 'postgresql' in database_url:
        print("✅ Primary database: PostgreSQL (Supabase)")
        try:
            import psycopg2
            conn = psycopg2.connect(database_url)
            cur = conn.cursor()
            
            # Test basic queries
            cur.execute('SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = %s', ('public',))
            table_count = cur.fetchone()[0]
            print(f"📊 Tables found: {table_count}")
            
            # Test user table
            try:
                cur.execute('SELECT COUNT(*) FROM "user"')
                user_count = cur.fetchone()[0]
                print(f"👥 Users in database: {user_count}")
            except:
                print("⚠️  User table not found - run create_db_and_tables()")
            
            cur.close()
            conn.close()
            print("✅ Supabase connection working!")
            return True
            
        except Exception as e:
            print(f"❌ Supabase connection failed: {e}")
            return False
    else:
        print("⚠️  Fallback database: SQLite")
        print("💡 Run setup to configure Supabase")
        return False

def main():
    """Main setup function"""
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        test_configuration()
    else:
        print("Choose an option:")
        print("1. Setup Supabase (recommended)")
        print("2. Test current configuration")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            if setup_supabase():
                print("\n🎉 Setup complete! Your AI Agent is now using Supabase as primary database.")
                print("🚀 Start the server with: python scripts/start_server.py")
            else:
                print("\n❌ Setup failed. Check the errors above and try again.")
        elif choice == '2':
            test_configuration()
        else:
            print("👋 Goodbye!")

if __name__ == "__main__":
    main()