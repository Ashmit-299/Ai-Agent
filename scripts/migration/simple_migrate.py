#!/usr/bin/env python3
"""Simple migration using raw SQL for Supabase"""

from dotenv import load_dotenv
load_dotenv()

import os
import json
import time
import uuid
from pathlib import Path
from sqlmodel import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=True)

def migrate_files():
    """Migrate files using raw SQL"""
    
    bucket_path = Path("bucket")
    migrated = 0
    
    with engine.connect() as conn:
        # Create demo user first
        try:
            conn.execute(text("""
                INSERT INTO "user" (user_id, username, password_hash, email, created_at) 
                VALUES ('demo001', 'demo', 'demo_hash', 'demo@example.com', :created_at)
                ON CONFLICT (user_id) DO NOTHING
            """), {"created_at": time.time()})
            conn.commit()
            print("Demo user ready")
        except Exception as e:
            print(f"User creation: {e}")
        
        # Migrate uploads
        uploads_path = bucket_path / "uploads"
        if uploads_path.exists():
            for file_path in uploads_path.glob("*"):
                if file_path.is_file() and not file_path.name.endswith('.json'):
                    insert_content(conn, file_path, "upload")
                    migrated += 1
        
        # Migrate videos  
        videos_path = bucket_path / "videos"
        if videos_path.exists():
            for file_path in videos_path.glob("*.mp4"):
                insert_content(conn, file_path, "video")
                migrated += 1
        
        # Migrate scripts
        scripts_path = bucket_path / "scripts"
        if scripts_path.exists():
            for file_path in scripts_path.glob("*.txt"):
                insert_content(conn, file_path, "script")
                migrated += 1
    
    print(f"Migrated {migrated} files to Supabase")

def insert_content(conn, file_path: Path, content_type: str):
    """Insert content using raw SQL"""
    try:
        content_id = uuid.uuid4().hex[:12]
        
        # Determine MIME type
        if file_path.suffix.lower() == '.mp4':
            mime_type = 'video/mp4'
        elif file_path.suffix.lower() == '.txt':
            mime_type = 'text/plain'
        elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            mime_type = 'image/jpeg'
        else:
            mime_type = 'application/octet-stream'
        
        conn.execute(text("""
            INSERT INTO content (
                content_id, uploader_id, title, description, file_path, 
                content_type, duration_ms, uploaded_at, authenticity_score, 
                current_tags, views, likes, shares
            ) VALUES (
                :content_id, :uploader_id, :title, :description, :file_path,
                :content_type, :duration_ms, :uploaded_at, :authenticity_score,
                :current_tags, :views, :likes, :shares
            )
        """), {
            "content_id": content_id,
            "uploader_id": "demo001", 
            "title": file_path.stem,
            "description": f"Migrated {content_type} from bucket",
            "file_path": str(file_path),
            "content_type": mime_type,
            "duration_ms": 0,
            "uploaded_at": time.time(),
            "authenticity_score": 0.8,
            "current_tags": json.dumps([content_type, "migrated"]),
            "views": 0,
            "likes": 0, 
            "shares": 0
        })
        conn.commit()
        print(f"Migrated: {file_path.name}")
        
    except Exception as e:
        print(f"Failed to migrate {file_path.name}: {e}")

if __name__ == "__main__":
    print("Starting simple migration to Supabase...")
    migrate_files()
    print("Migration complete! Check Supabase Table Editor")