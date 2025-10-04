#!/usr/bin/env python3
"""
Simplified CDN Routes - Easy to understand and use
"""
import os
import time
import secrets
import hashlib
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse

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

# Simple in-memory token storage (use Redis in production)
upload_tokens = {}

router = APIRouter(prefix="/cdn", tags=["CDN & File Management"])

@router.get("/upload-url")
async def get_upload_url(
    filename: str,
    content_type: str = "application/octet-stream",
    current_user = Depends(get_current_user_required)
):
    """Get upload URL - Simple version that always works"""
    
    # Generate secure upload token
    upload_token = secrets.token_urlsafe(32)
    
    # Store token with expiry (1 hour)
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
        "upload_url": f"upload/{upload_token}",
        "method": "POST",
        "expires_in": 3600,
        "max_file_size_mb": 100,
        "instructions": [
            "1. POST your file to the upload_url",
            "2. Use multipart/form-data",
            "3. File field name: 'file'",
            "4. Include your JWT token in Authorization header"
        ],
        "example": f"curl -X POST '/cdn/upload/{upload_token}' -H 'Authorization: Bearer YOUR_TOKEN' -F 'file=@{filename}'"
    }

@router.post("/upload/{upload_token}")
async def upload_file(
    upload_token: str,
    file: UploadFile = File(...),
    current_user = Depends(get_current_user_required)
):
    """Upload file using upload token - Simple and reliable"""
    
    # Validate token
    if upload_token not in upload_tokens:
        raise HTTPException(status_code=400, detail="Invalid upload token")
    
    token_data = upload_tokens[upload_token]
    
    # Check expiry
    if time.time() > token_data['expires_at']:
        del upload_tokens[upload_token]
        raise HTTPException(status_code=400, detail="Upload token expired")
    
    # Check if already used
    if token_data['used']:
        raise HTTPException(status_code=400, detail="Upload token already used")
    
    # Verify user
    if token_data['user_id'] != current_user.user_id:
        raise HTTPException(status_code=403, detail="Token belongs to different user")
    
    # Read and validate file
    file_content = await file.read()
    max_size = 100 * 1024 * 1024  # 100MB
    
    if len(file_content) > max_size:
        raise HTTPException(status_code=413, detail=f"File too large. Max: {max_size/1024/1024}MB")
    
    # Generate content ID
    content_hash = hashlib.sha256(file_content).hexdigest()[:12]
    content_id = f"{content_hash}_{int(time.time())}"
    
    # Save file locally (simple approach)
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{content_id}_{file.filename}"
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Mark token as used
    upload_tokens[upload_token]['used'] = True
    
    # Save to database (simple SQLite)
    try:
        import sqlite3
        conn = sqlite3.connect('data.db')
        with conn:
            cur = conn.cursor()
            # Create table if not exists
            cur.execute("""
                CREATE TABLE IF NOT EXISTS content (
                    content_id TEXT PRIMARY KEY,
                    uploader_id TEXT,
                    title TEXT,
                    description TEXT,
                    file_path TEXT,
                    content_type TEXT,
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
                INSERT OR REPLACE INTO content 
                (content_id, uploader_id, title, file_path, content_type, uploaded_at, authenticity_score, current_tags, views, likes, shares)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                content_id, current_user.user_id, file.filename, file_path, 
                file.content_type, time.time(), 0.8, '[]', 0, 0, 0
            ))
        conn.close()
    except Exception as db_error:
        print(f"Database save failed: {db_error}")
    
    return {
        "status": "success",
        "content_id": content_id,
        "filename": file.filename,
        "file_size": len(file_content),
        "file_path": file_path,
        "download_url": f"/cdn/download/{content_id}",
        "stream_url": f"/cdn/stream/{content_id}"
    }

@router.get("/download/{content_id}")
async def download_file(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Download file by content ID - Simple and works"""
    
    try:
        # Get file path from database
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT file_path, title FROM content WHERE content_id = ?", (content_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, title = result
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            file_path,
            filename=title or os.path.basename(file_path),
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/stream/{content_id}")
async def stream_file(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Stream file by content ID - Simple streaming"""
    
    try:
        # Get file path from database
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT file_path, content_type FROM content WHERE content_id = ?", (content_id,))
        result = cur.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, content_type = result
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            file_path,
            media_type=content_type or 'application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streaming failed: {str(e)}")

@router.get("/list")
async def list_files(
    limit: int = 20,
    current_user = Depends(get_current_user_required)
):
    """List uploaded files for current user"""
    
    try:
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""
            SELECT content_id, title, content_type, uploaded_at, views, likes
            FROM content 
            WHERE uploader_id = ?
            ORDER BY uploaded_at DESC
            LIMIT ?
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
                "download_url": f"/cdn/download/{row[0]}",
                "stream_url": f"/cdn/stream/{row[0]}"
            })
        
        return {
            "files": files,
            "total": len(files),
            "user_id": current_user.user_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")

@router.delete("/delete/{content_id}")
async def delete_file(
    content_id: str,
    current_user = Depends(get_current_user_required)
):
    """Delete file by content ID"""
    
    try:
        # Get file info from database
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("SELECT file_path, uploader_id FROM content WHERE content_id = ?", (content_id,))
        result = cur.fetchone()
        
        if not result:
            conn.close()
            raise HTTPException(status_code=404, detail="Content not found")
        
        file_path, uploader_id = result
        
        # Check ownership
        if uploader_id != current_user.user_id:
            conn.close()
            raise HTTPException(status_code=403, detail="Not your file")
        
        # Delete from database
        cur.execute("DELETE FROM content WHERE content_id = ?", (content_id,))
        conn.commit()
        conn.close()
        
        # Delete file from disk
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as file_error:
            print(f"File deletion failed: {file_error}")
        
        return {
            "status": "success",
            "message": "File deleted successfully",
            "content_id": content_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

@router.get("/info/{content_id}")
async def get_file_info(
    content_id: str,
    current_user = Depends(get_current_user_optional)
):
    """Get file information"""
    
    try:
        import sqlite3
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute("""
            SELECT content_id, title, content_type, uploaded_at, authenticity_score, 
                   current_tags, views, likes, shares, uploader_id
            FROM content WHERE content_id = ?
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
            "download_url": f"/cdn/download/{content_id}",
            "stream_url": f"/cdn/stream/{content_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Info failed: {str(e)}")