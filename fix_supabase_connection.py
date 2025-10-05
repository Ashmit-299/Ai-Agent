#!/usr/bin/env python3
"""
Fix Supabase Connection - Get correct connection string
"""

def fix_supabase():
    print("🔧 Fix Supabase Connection")
    print("=" * 40)
    
    print("Your Supabase project: dusqpdhojbgfxwflukhc")
    print("\n📋 Go to your Supabase Dashboard:")
    print("1. https://supabase.com/dashboard")
    print("2. Select your project: dusqpdhojbgfxwflukhc")
    print("3. Go to Settings → Database")
    print("4. Find 'Connection string' section")
    print("5. Copy the 'URI' connection string")
    
    print("\n🔍 It should look like ONE of these:")
    print("Format 1: postgresql://postgres.dusqpdhojbgfxwflukhc:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres")
    print("Format 2: postgresql://postgres:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:5432/postgres")
    print("Format 3: postgresql://postgres:[PASSWORD]@db.dusqpdhojbgfxwflukhc.supabase.co:5432/postgres")
    
    connection_string = input("\n📝 Paste your EXACT connection string here: ").strip()
    
    if not connection_string.startswith('postgresql://'):
        print("❌ Invalid connection string format")
        return False
    
    # Test connection
    try:
        import psycopg2
        test_conn = psycopg2.connect(connection_string)
        test_conn.close()
        print("✅ Connection test successful!")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n💡 Try these alternatives:")
        
        # Extract password from provided string
        import re
        password_match = re.search(r':([^@]+)@', connection_string)
        if password_match:
            password = password_match.group(1)
            
            alternatives = [
                f"postgresql://postgres.dusqpdhojbgfxwflukhc:{password}@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
                f"postgresql://postgres:{password}@aws-0-us-east-1.pooler.supabase.com:5432/postgres",
                f"postgresql://postgres:{password}@db.dusqpdhojbgfxwflukhc.supabase.co:5432/postgres"
            ]
            
            for i, alt in enumerate(alternatives, 1):
                try:
                    test_conn = psycopg2.connect(alt)
                    test_conn.close()
                    connection_string = alt
                    print(f"✅ Alternative {i} works!")
                    break
                except:
                    print(f"❌ Alternative {i} failed")
            else:
                return False
    
    # Update .env
    import os
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
    
    # Update DATABASE_URL
    lines = env_content.split('\n')
    updated = False
    for i, line in enumerate(lines):
        if line.startswith("DATABASE_URL=") or line.startswith("# DATABASE_URL="):
            lines[i] = f"DATABASE_URL={connection_string}"
            updated = True
            break
    
    if not updated:
        lines.append(f"DATABASE_URL={connection_string}")
    
    # Write back
    with open('.env', 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ Supabase connection string saved!")
    
    # Create tables
    try:
        from core.database import create_db_and_tables
        create_db_and_tables()
        print("✅ Supabase tables created!")
    except Exception as e:
        print(f"⚠️  Table creation: {e}")
    
    return True

if __name__ == "__main__":
    fix_supabase()