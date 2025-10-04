#!/usr/bin/env python3
"""Migrate all bucket data to Supabase PostgreSQL"""

from dotenv import load_dotenv
load_dotenv()  # Load first

import os
import json
import time
import uuid
from pathlib import Path
from sqlmodel import Session
from ..core.database import engine
from ..core.models import User, Content, Feedback

def migrate_bucket_data():
    """Migrate all files from bucket to Supabase"""
    
    # Create demo user if not exists
    with Session(engine) as session:
        demo_user = session.get(User, "demo001")
        if not demo_user:
            demo_user = User(
                user_id="demo001",
                username="demo",
                password_hash="demo_hash",
                email="demo@example.com"
            )
            session.add(demo_user)
            session.commit()
            print("Created demo user")
    
    bucket_path = Path("bucket")
    if not bucket_path.exists():
        print("❌ Bucket directory not found")
        return
    
    migrated_count = 0
    
    # Migrate uploads
    uploads_path = bucket_path / "uploads"
    if uploads_path.exists():
        for file_path in uploads_path.glob("*"):
            if file_path.is_file():
                migrate_file(file_path, "upload", session)
                migrated_count += 1
    
    # Migrate videos
    videos_path = bucket_path / "videos"
    if videos_path.exists():
        for file_path in videos_path.glob("*"):
            if file_path.is_file():
                migrate_file(file_path, "video", session)
                migrated_count += 1
    
    # Migrate scripts
    scripts_path = bucket_path / "scripts"
    if scripts_path.exists():
        for file_path in scripts_path.glob("*"):
            if file_path.is_file():
                migrate_file(file_path, "script", session)
                migrated_count += 1
    
    print(f"Migrated {migrated_count} files to Supabase")

def migrate_file(file_path: Path, content_type: str, session):
    """Migrate single file to Supabase"""
    try:
        with Session(engine) as session:
            content_id = uuid.uuid4().hex[:12]
            
            # Determine content type
            if file_path.suffix.lower() in ['.mp4', '.avi', '.mov']:
                mime_type = 'video/mp4'
            elif file_path.suffix.lower() in ['.txt', '.md']:
                mime_type = 'text/plain'
            elif file_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                mime_type = 'image/jpeg'
            else:
                mime_type = 'application/octet-stream'
            
            content = Content(
                content_id=content_id,
                uploader_id="demo001",
                title=file_path.stem,
                description=f"Migrated {content_type} from bucket",
                file_path=str(file_path),
                content_type=mime_type,
                authenticity_score=0.8,
                current_tags=json.dumps([content_type, "migrated"]),
                uploaded_at=time.time()
            )
            
            session.add(content)
            session.commit()
            print(f"Migrated: {file_path.name}")
            
    except Exception as e:
        print(f"Failed to migrate {file_path.name}: {e}")

if __name__ == "__main__":
    print("Starting bucket to Supabase migration...")
    migrate_bucket_data()
    print("Migration complete! Check Supabase Table Editor")