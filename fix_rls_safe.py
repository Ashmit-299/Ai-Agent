#!/usr/bin/env python3
"""
Safely apply RLS fixes to existing Supabase tables
"""

import os
import psycopg2
from dotenv import load_dotenv

def get_existing_tables(cur):
    """Get list of existing tables in public schema"""
    cur.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename NOT LIKE 'pg_%'
        AND tablename != 'information_schema'
    """)
    return [row[0] for row in cur.fetchall()]

def apply_rls_to_table(cur, table_name):
    """Apply RLS to a specific table"""
    try:
        # Enable RLS
        cur.execute(f'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY;')
        print(f"  Enabled RLS on {table_name}")
        
        # Apply table-specific policies
        if table_name == 'enhanced_analytics' or table_name == 'analytics':
            # Analytics tables - users can access their own data
            cur.execute(f'''
                CREATE POLICY "Users can view their own analytics" ON public."{table_name}"
                FOR SELECT USING (auth.uid()::text = user_id OR user_id IS NULL);
            ''')
            cur.execute(f'''
                CREATE POLICY "Users can insert their own analytics" ON public."{table_name}"
                FOR INSERT WITH CHECK (auth.uid()::text = user_id OR user_id IS NULL);
            ''')
            cur.execute(f'''
                CREATE POLICY "Service role can manage all analytics" ON public."{table_name}"
                FOR ALL USING (auth.role() = 'service_role');
            ''')
            
        elif table_name == 'user':
            # User table - users can access their own profile
            cur.execute(f'''
                CREATE POLICY "Users can view their own profile" ON public."{table_name}"
                FOR SELECT USING (auth.uid()::text = user_id);
            ''')
            cur.execute(f'''
                CREATE POLICY "Service role can manage all users" ON public."{table_name}"
                FOR ALL USING (auth.role() = 'service_role');
            ''')
            
        elif table_name == 'content':
            # Content table - public read, owner write
            cur.execute(f'''
                CREATE POLICY "Anyone can view content" ON public."{table_name}"
                FOR SELECT USING (true);
            ''')
            cur.execute(f'''
                CREATE POLICY "Users can manage their own content" ON public."{table_name}"
                FOR ALL USING (auth.uid()::text = uploader_id OR auth.role() = 'service_role');
            ''')
            
        elif table_name == 'feedback':
            # Feedback table - public read, owner write
            cur.execute(f'''
                CREATE POLICY "Anyone can view feedback" ON public."{table_name}"
                FOR SELECT USING (true);
            ''')
            cur.execute(f'''
                CREATE POLICY "Users can manage their own feedback" ON public."{table_name}"
                FOR ALL USING (auth.uid()::text = user_id OR auth.role() = 'service_role');
            ''')
            
        elif table_name == 'script':
            # Script table - public read, owner write
            cur.execute(f'''
                CREATE POLICY "Anyone can view scripts" ON public."{table_name}"
                FOR SELECT USING (true);
            ''')
            cur.execute(f'''
                CREATE POLICY "Users can manage their own scripts" ON public."{table_name}"
                FOR ALL USING (auth.uid()::text = user_id OR auth.role() = 'service_role');
            ''')
            
        else:
            # Default policy for other tables - service role only
            cur.execute(f'''
                CREATE POLICY "Service role only" ON public."{table_name}"
                FOR ALL USING (auth.role() = 'service_role');
            ''')
        
        print(f"  Applied policies to {table_name}")
        return True
        
    except Exception as e:
        print(f"  Error with {table_name}: {e}")
        return False

def main():
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
        print("DATABASE_URL not found or not PostgreSQL")
        return False
    
    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Get existing tables
        tables = get_existing_tables(cur)
        print(f"Found tables: {tables}")
        
        # Apply RLS to each table
        print("\nApplying RLS fixes...")
        success_count = 0
        
        for table in tables:
            if apply_rls_to_table(cur, table):
                success_count += 1
        
        # Grant permissions
        print("\nGranting permissions...")
        cur.execute("GRANT USAGE ON SCHEMA public TO authenticated;")
        cur.execute("GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;")
        cur.execute("GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;")
        
        conn.commit()
        
        # Verify RLS status
        print("\nVerifying RLS status...")
        cur.execute("""
            SELECT tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
            ORDER BY tablename;
        """)
        
        results = cur.fetchall()
        print("\nRLS Status:")
        for table, rls_enabled in results:
            status = "ENABLED" if rls_enabled else "DISABLED"
            print(f"  {table}: {status}")
        
        cur.close()
        conn.close()
        
        print(f"\nSuccess! Applied RLS to {success_count}/{len(tables)} tables")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Supabase RLS Security Fix (Safe Mode)")
    print("=" * 40)
    main()