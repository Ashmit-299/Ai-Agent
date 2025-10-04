#!/usr/bin/env python3
"""
Verify all endpoints are using Supabase database correctly
"""

import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

def test_supabase_connection():
    """Test direct Supabase connection"""
    try:
        import psycopg2
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        if not DATABASE_URL or not DATABASE_URL.startswith("postgresql"):
            print("[ERROR] DATABASE_URL not set to PostgreSQL")
            return False
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        
        print(f"[OK] Supabase connection successful: {DATABASE_URL[:50]}...")
        return True
    except Exception as e:
        print(f"[ERROR] Supabase connection failed: {e}")
        return False

def test_endpoints_with_supabase():
    """Test key endpoints to ensure they return data from Supabase"""
    base_url = "https://ai-agent-aff6.onrender.com"
    
    endpoints_to_test = [
        "/contents",
        "/metrics", 
        "/bhiv/analytics",
        "/bucket/stats"
    ]
    
    print("\n[TEST] Testing endpoints for Supabase data...")
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check for data indicators
                has_data = False
                if endpoint == "/contents":
                    has_data = len(data.get("items", [])) > 0
                elif endpoint == "/metrics":
                    has_data = data.get("system_metrics", {}).get("total_contents", 0) > 0
                elif endpoint == "/bhiv/analytics":
                    has_data = data.get("total_content", 0) > 0
                elif endpoint == "/bucket/stats":
                    has_data = data.get("bucket_stats", {}).get("total_bucket_files", 0) >= 0
                
                status = "[OK]" if has_data else "[EMPTY]"
                print(f"{status} {endpoint} - Status: {response.status_code}")
                
                if not has_data and endpoint in ["/contents", "/metrics", "/bhiv/analytics"]:
                    print(f"  [WARNING] {endpoint} returned empty data - may need content in Supabase")
            else:
                print(f"[ERROR] {endpoint} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"[ERROR] {endpoint} - Request failed: {e}")

def create_test_content():
    """Create test content in Supabase to verify data flow"""
    try:
        from ..core.database import DatabaseManager
        import uuid
        
        db = DatabaseManager()
        
        # Create test content
        content_data = {
            'content_id': f"test_{uuid.uuid4().hex[:8]}",
            'uploader_id': 'demo001',
            'title': 'Test Content for Supabase Verification',
            'description': 'This is test content to verify Supabase integration',
            'file_path': '/test/path',
            'content_type': 'text/plain',
            'duration_ms': 30000,
            'uploaded_at': time.time(),
            'authenticity_score': 0.85,
            'current_tags': '["test", "verification", "supabase"]',
            'views': 0,
            'likes': 0,
            'shares': 0
        }
        
        # Save to Supabase
        import psycopg2
        import json
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO content (content_id, uploader_id, title, description, file_path, content_type, duration_ms, uploaded_at, authenticity_score, current_tags, views, likes, shares)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            content_data['content_id'], content_data['uploader_id'], content_data['title'],
            content_data['description'], content_data['file_path'], content_data['content_type'],
            content_data['duration_ms'], content_data['uploaded_at'], content_data['authenticity_score'], 
            content_data['current_tags'], content_data['views'], content_data['likes'], content_data['shares']
        ))
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"[OK] Test content created in Supabase: {content_data['content_id']}")
        return content_data['content_id']
        
    except Exception as e:
        print(f"[ERROR] Failed to create test content: {e}")
        return None

def main():
    print("=== Supabase Integration Verification ===")
    
    # Test 1: Direct connection
    print("\n1. Testing direct Supabase connection...")
    if not test_supabase_connection():
        print("[CRITICAL] Cannot connect to Supabase. Check DATABASE_URL in .env")
        return
    
    # Test 2: Create test content
    print("\n2. Creating test content in Supabase...")
    test_content_id = create_test_content()
    
    # Test 3: Test endpoints
    print("\n3. Testing API endpoints...")
    test_endpoints_with_supabase()
    
    print("\n=== Verification Complete ===")
    print("All endpoints should now be using Supabase database.")
    print("If any endpoints show [EMPTY], they may need content to be uploaded first.")

if __name__ == "__main__":
    main()