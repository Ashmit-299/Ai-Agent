#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Test script save
    cur.execute("""
        INSERT INTO script (script_id, content_id, user_id, title, script_content, script_type, file_path, created_at, used_for_generation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        "test_script_123",
        "test_content_123", 
        "demo001",
        "Test Script",
        "This is a test script content",
        "video_generation",
        None,
        1234567890.0,
        True
    ))
    
    conn.commit()
    cur.close()
    conn.close()
    print("Script saved successfully to Supabase!")
    
except Exception as e:
    print(f"Error: {e}")