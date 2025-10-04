#!/usr/bin/env python3
"""
Supabase CDN Routes - Fixed URL encoding issue
"""
import os
import time
import secrets
import hashlib
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import StreamingResponse
import io

try:
    from .auth import get_current_user_required, get_current_user_optional
except ImportError:
    async def get_current_user_required():
        class User:
            user_id = "demo001"
            username = "demo"
        return User()
    
    async def get_current_user_optional():
        return None

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Simple in-memory token storage
upload_tokens = {}

router = APIRouter(prefix="/cdn", tags=["CDN & File Management"])

def get_supabase_client():
    """Get Supabase client for storage operations"""
    try:
        from supabase import create_client, Client
        return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    except ImportError:
        raise HTTPException(status_code=500, detail="Supabase client not installed. Run: pip install supabase")

@router.get("/upload-url")
async def get_upload_url(
    filename: str,
    content_type: str = "application/octet-stream",
    current_user = Depends(get_current_user_required)
):
    """Get upload URL for Supabase storage"""
    
    upload_token = secrets.token_urlsafe(32)
    
    upload_tokens[upload_token] = {
        'user_id': current_user.user_id,
        'filename': filename,
        'content_type': content_type,
        'expires_at': time.time() + 3600,
        'used': False
    }
    
    # Clean expired tokens
    current_time = time.time()
    expired = [token for token, data in upload_tokens.items() if data['expires_at'] < current_time]
    for token in expired:
        del upload_tokens[token]
    
    return {
        "upload_url": f"upload/{upload_token}",  # Fixed: No leading slash
        "method": "POST",
        "expires_in": 3600,
        "max_file_size_mb": 100,
        "storage": "supabase"
    }

@router.post("/upload/{upload_token}")
async def upload_file(
    upload_token: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user_required)
):
    """Upload file to Supabase storage"""
    
    if upload_token not in upload_tokens:
        raise HTTPException(status_code=400, detail="Invalid upload token")
    
    token_data = upload_tokens[upload_token]
    
    if time.time() > token_data['expires_at']:
        del upload_tokens[upload_token]
        raise HTTPException(status_code=400, detail="Upload token expired")
    
    if token_data['used']:
        raise HTTPException(status_code=400, detail="Upload token already used")
    
    if token_data['user_id'] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Token belongs to different user")
    
    file_content = await file.read()
    max_size = 100 * 1024 * 1024  # 100MB
    
    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail=f"File too large. Max: {max_size/1024/1024}MB")
    
    content_hash = hashlib.sha256(file_content).hexdigest()[:12]
    content_id = f"{content_hash}_{int(time.time())}"
    storage_path = f"uploads/{current_user.user_id}/{content_id}_{file.filename}"
    
    try:
        # Upload to Supabase Storage
        supabase = get_supabase_client()
        
        result = supabase.storage.from_("ai-agent-files").upload(
            storage_path,
            file_content,
            file_options={"content-type": file.content_type}
        )
        
        if result.error:
            raise HTTPException(status_code=500, detail=f"Supabase upload failed: {result.error}")
        
        public_url = supabase.storage.from_("ai-agent-files").get_public_url(storage_path)
        
        upload_tokens[upload_token]['used'] = True
        
        # Save metadata to Supabase PostgreSQL
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        with conn:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    content_id TEXT PRIMARY KEY,
                    uploader_id TEXT,
                    title TEXT,
                    description TEXT,
                    file_path TEXT,
                    storage_url TEXT,
                    content_type TEXT,
                    file_size INTEGER,
                    duration_ms INTEGER,
                    uploaded_at REAL,
                    authenticity_score REAL,
                    current_tags TEXT,
                    views INTEGER DEFAULT 0,
                    likes INTEGER DEFAULT 0,
                    shares INTEGER DEFAULT 0
                )
            """)
            cur.execute("""
                INSERT INTO content 
                (content_id, uploader_id, title, file_path, storage_url, content_type, file_size, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                content_id, current_user.user_id, file.filename, storage_path, public_url,
                file.content_type, len(file_content), time.time(), 0.8, '[]', 0, 0, 0
            ))
        conn.close()
        
        return {
            "status": "success",
            "content_id": content_id,
            "filename": file.filename,
            "file_size": len(file_content),
            "storage_path": storage_path,
            "storage_url": public_url,
            "download_url": f"/cdn/download/{content_id}",
            "stream_url": f"/cdn/stream/{content_id}",
            "storage": "supabase"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/download/{content_id}")
async def download_file(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Download file from Supabase storage"""
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT file_path, title, storage_url FROM content WHERE content_id = %s", (content_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, title, storage_url = result
        
        supabase = get_supabase_client()
        file_data = supabase.storage.from_("ai-agent-files").download(file_path)
        
        if not file_data:
            raise HTTPException(status_code=404, detail="File not found in storage")
        
        return StreamingResponse(
            io.BytesIO(file_data),
            media_type='application/octet-stream',
            headers={"Content-Disposition": f"attachment; filename={title}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/stream/{content_id}")
async def stream_file(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Stream file from Supabase storage"""
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT file_path, content_type, storage_url FROM content WHERE content_id = %s", (content_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, content_type, storage_url = result
        
        if storage_url:
            from fastapi.responses import RedirectResponse
            return RedirectResponse(url=storage_url)
        else:
            supabase = get_supabase_client()
            file_data = supabase.storage.from_("ai-agent-files").download(file_path)
            
            if not file_data:
                raise HTTPException(status_code=404, detail="File not found in storage")
            
            return StreamingResponse(
                io.BytesIO(file_data),
                media_type=content_type or 'application/octet-stream'
            )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@router.get("/list")
async def list_files(
    limit: int = 20,
    current_user = Depends(get_current_user_required)
):
    """List uploaded files for current user from Supabase"""
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT content_id, title, content_type, uploaded_at, views, likes, file_size, storage_url
            FROM content 
            WHERE uploader_id = %s
            ORDER BY uploaded_at DESC
            LIMIT %s
        """, (current_user.user_id, limit))
        results = cur.fetchall()
        conn.close()
        
        files = []
        for row in results:
            files.append({
                "content_id": row[0],
                "filename": row[1],
                "content_type": row[2],
                "uploaded_at": row[3],
                "views": row[4],
                "likes": row[5],
                "file_size": row[6],
                "storage_url": row[7],
                "download_url": f"/cdn/download/{row[0]}",
                "stream_url": f"/cdn/stream/{row[0]}"
            })
        
        return {
            "files": files,
            "total": len(files),
            "user_id": current_user.user_id,
            "storage": "supabase"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")

@router.delete("/delete/{content_id}")
async def delete_file(
    content_id: str,
    current_user = Depends(get_current_user_required)
):
    """Delete file from Supabase storage and database"""
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT file_path, uploader_id FROM content WHERE content_id = %s", (content_id,))
        result = cur.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, uploader_id = result
        
        if uploader_id != current_user.user_id:
            conn.close()
            raise HTTPException(status_code=403, detail="Not your file")
        
        try:
            supabase = get_supabase_client()
            supabase.storage.from_("ai-agent-files").remove([file_path])
        except Exception as storage_error:
            print(f"Storage deletion failed: {storage_error}")
        
        cur.execute("DELETE FROM content WHERE content_id = %s", (content_id,))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "File deleted successfully",
            "content_id": content_id,
            "storage": "supabase"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/info/{content_id}")
async def get_file_info(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Get file information from Supabase"""
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("""
            SELECT content_id, title, content_type, uploaded_at, authenticity_score, 
                   current_tags, views, likes, shares, uploader_id, file_size, storage_url
            FROM content WHERE content_id = %s
        """, (content_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return {
            "content_id": result[0],
            "filename": result[1],
            "content_type": result[2],
            "uploaded_at": result[3],
            "authenticity_score": result[4],
            "tags": result[5],
            "views": result[6],
            "likes": result[7],
            "shares": result[8],
            "uploader_id": result[9],
            "file_size": result[10],
            "storage_url": result[11],
            "download_url": f"/cdn/download/{content_id}",
            "stream_url": f"/cdn/stream/{content_id}",
            "storage": "supabase"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info failed: {str(e)}")