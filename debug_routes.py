#!/usr/bin/env python3
"""
Debug script for routes.py - identifies common issues and performance bottlenecks
"""

import os
import sys
import time
import json
import sqlite3
from pathlib import Path

def check_imports():
    """Check if all required imports are available"""
    issues = []
    
    try:
        import app.routes
        print("[OK] Routes module imports successfully")
    except ImportError as e:
        issues.append(f"Import error in routes: {e}")
    
    try:
        from core.database import DatabaseManager
        print("[OK] DatabaseManager available")
    except ImportError:
        issues.append("DatabaseManager not available - using SQLite fallback")
    
    try:
        from app.agent import RLAgent
        print("[OK] RLAgent available")
    except ImportError:
        issues.append("RLAgent not available")
    
    return issues

def check_database():
    """Check database connectivity and tables"""
    issues = []
    
    # Check SQLite
    try:
        with sqlite3.connect('data.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cur.fetchall()]
            print(f"[OK] SQLite tables: {tables}")
            
            if 'content' not in tables:
                issues.append("Content table missing in SQLite")
            if 'feedback' not in tables:
                issues.append("Feedback table missing in SQLite")
                
    except Exception as e:
        issues.append(f"SQLite connection failed: {e}")
    
    # Check Supabase
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL and 'postgresql' in DATABASE_URL:
            import psycopg2
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()
            cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            tables = [row[0] for row in cur.fetchall()]
            print(f"[OK] PostgreSQL tables: {tables}")
            cur.close()
            conn.close()
        else:
            issues.append("PostgreSQL DATABASE_URL not configured")
    except Exception as e:
        issues.append(f"PostgreSQL connection failed: {e}")
    
    return issues

def check_file_structure():
    """Check required directories and files"""
    issues = []
    
    required_dirs = ['bucket', 'bucket/uploads', 'bucket/videos', 'bucket/scripts', 'uploads']
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            print(f"[OK] Created directory: {dir_path}")
        else:
            print(f"[OK] Directory exists: {dir_path}")
    
    required_files = ['agent_state.json']
    for file_path in required_files:
        if not os.path.exists(file_path):
            if file_path == 'agent_state.json':
                with open(file_path, 'w') as f:
                    json.dump({}, f)
                print(f"[OK] Created file: {file_path}")
        else:
            print(f"[OK] File exists: {file_path}")
    
    return issues

def test_endpoints():
    """Test critical endpoint functions"""
    issues = []
    
    try:
        import app.routes
        validate_environment = app.routes.validate_environment
        compute_authenticity = app.routes.compute_authenticity
        suggest_tags = app.routes.suggest_tags
        
        # Test validate_environment
        result = validate_environment()
        if result['validation']['valid']:
            print("[OK] Environment validation works")
        else:
            issues.append("Environment validation failed")
        
        # Test utility functions
        test_file = 'test_file.txt'
        with open(test_file, 'w') as f:
            f.write("test content")
        
        auth_score = compute_authenticity(test_file, "test", "description")
        if 0 <= auth_score <= 1:
            print(f"[OK] Authenticity computation works: {auth_score}")
        else:
            issues.append(f"Invalid authenticity score: {auth_score}")
        
        tags = suggest_tags("test title", "test description")
        if isinstance(tags, list):
            print(f"[OK] Tag suggestion works: {tags}")
        else:
            issues.append("Tag suggestion failed")
        
        os.remove(test_file)
        
    except Exception as e:
        issues.append(f"Endpoint testing failed: {e}")
    
    return issues

def performance_check():
    """Check performance of key operations"""
    print("\n=== Performance Check ===")
    
    # Database query performance
    start_time = time.time()
    try:
        with sqlite3.connect('data.db') as conn:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM content')
            count = cur.fetchone()[0]
        query_time = time.time() - start_time
        print(f"[OK] Database query time: {query_time:.3f}s (count: {count})")
    except Exception as e:
        print(f"[ERROR] Database query failed: {e}")
    
    # File I/O performance
    start_time = time.time()
    test_data = "x" * 1024 * 100  # 100KB
    with open('perf_test.txt', 'w') as f:
        f.write(test_data)
    with open('perf_test.txt', 'r') as f:
        data = f.read()
    os.remove('perf_test.txt')
    io_time = time.time() - start_time
    print(f"[OK] File I/O time (100KB): {io_time:.3f}s")

def main():
    """Run all diagnostic checks"""
    print("=== AI Agent Routes Diagnostics ===\n")
    
    all_issues = []
    
    print("=== Import Check ===")
    all_issues.extend(check_imports())
    
    print("\n=== Database Check ===")
    all_issues.extend(check_database())
    
    print("\n=== File Structure Check ===")
    all_issues.extend(check_file_structure())
    
    print("\n=== Endpoint Test ===")
    all_issues.extend(test_endpoints())
    
    performance_check()
    
    print("\n=== Summary ===")
    if all_issues:
        print("Issues found:")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. {issue}")
    else:
        print("[OK] All checks passed!")
    
    print(f"\nDiagnostics completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()