#!/usr/bin/env python3
"""
Get correct Supabase connection string from Supabase dashboard
"""

def get_connection_string():
    print("🔗 Get Your Supabase Connection String")
    print("=" * 40)
    
    print("1. Go to your Supabase dashboard")
    print("2. Click on 'Settings' → 'Database'")
    print("3. Scroll down to 'Connection string'")
    print("4. Copy the 'URI' connection string")
    print("5. It should look like:")
    print("   postgresql://postgres.xxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    print("   OR")
    print("   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres")
    
    connection_string = input("\nPaste your connection string here: ").strip()
    
    if not connection_string.startswith('postgresql://'):
        print("❌ Invalid connection string")
        return False
    
    # Update .env
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update DATABASE_URL
    if "DATABASE_URL=" in env_content:
        lines = env_content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith("DATABASE_URL="):
                lines[i] = f"DATABASE_URL={connection_string}"
        env_content = '\n'.join(lines)
    else:
        env_content += f"\nDATABASE_URL={connection_string}"
    
    # Write .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Connection string saved!")
    
    # Test connection
    try:
        import psycopg2
        conn = psycopg2.connect(connection_string)
        conn.close()
        print("✅ Connection test successful!")
        
        # Create tables
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Database tables created!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    import os
    get_connection_string()