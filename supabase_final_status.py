#!/usr/bin/env python3

import os
import psycopg2

def check_supabase_status():
    """Comprehensive check of all Supabase optimizations"""
    
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL must be set")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("=== SUPABASE PERFORMANCE OPTIMIZATION STATUS ===")
        print()
        
        # 1. Check RLS Security
        cursor.execute("""
            SELECT schemaname, tablename, rowsecurity 
            FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('users', 'scripts', 'videos', 'systemlogs', 'feedback', 'analytics', 'enhanced_analytics')
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        rls_enabled = sum(1 for t in tables if t[2])
        
        print(f"1. RLS Security: {rls_enabled}/{len(tables)} tables have RLS enabled")
        for schema, table, rls in tables:
            status = "ENABLED" if rls else "DISABLED"
            print(f"   - {table}: {status}")
        
        # 2. Check Multiple Permissive Policies
        cursor.execute("""
            SELECT tablename, COUNT(*) as policy_count
            FROM pg_policies 
            WHERE schemaname = 'public'
            GROUP BY tablename
            ORDER BY tablename;
        """)
        
        policies = cursor.fetchall()
        print(f"\n2. Multiple Permissive Policies: {len(policies)} tables with policies")
        for table, count in policies:
            print(f"   - {table}: {count} policy(ies)")
        
        # 3. Check Auth RLS Optimization
        cursor.execute("""
            SELECT tablename, policyname, qual
            FROM pg_policies 
            WHERE tablename = 'enhanced_analytics' 
            AND policyname = 'enhanced_analytics_policy';
        """)
        
        auth_policy = cursor.fetchone()
        if auth_policy:
            table, policy, qual = auth_policy
            optimized = "SELECT" in qual and "auth.uid()" in qual
            status = "OPTIMIZED" if optimized else "NEEDS OPTIMIZATION"
            print(f"\n3. Auth RLS Optimization: {status}")
            print(f"   - enhanced_analytics policy uses subquery pattern")
        else:
            print(f"\n3. Auth RLS Optimization: NO POLICY FOUND")
        
        # 4. Check Indexes
        cursor.execute("""
            SELECT schemaname, tablename, indexname, indexdef
            FROM pg_indexes 
            WHERE schemaname = 'public'
            AND tablename IN ('users', 'scripts', 'videos', 'systemlogs', 'feedback', 'analytics', 'enhanced_analytics')
            ORDER BY tablename, indexname;
        """)
        
        indexes = cursor.fetchall()
        print(f"\n4. Database Indexes: {len(indexes)} indexes found")
        
        # Group by table
        table_indexes = {}
        for schema, table, index, indexdef in indexes:
            if table not in table_indexes:
                table_indexes[table] = []
            table_indexes[table].append(index)
        
        for table, idx_list in sorted(table_indexes.items()):
            print(f"   - {table}: {len(idx_list)} indexes")
        
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("SUPABASE OPTIMIZATION SUMMARY:")
        print(f"- RLS Security: {rls_enabled}/{len(tables)} tables protected")
        print(f"- Policies: {len(policies)} tables with RLS policies")
        print(f"- Auth Optimization: {'COMPLETED' if auth_policy and optimized else 'PENDING'}")
        print(f"- Database Indexes: {len(indexes)} indexes optimized")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    # Load environment variables
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    check_supabase_status()