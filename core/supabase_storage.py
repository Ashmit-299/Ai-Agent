#!/usr/bin/env python3
"""
Supabase Storage Integration for AI Agent
"""
import os
from typing import Optional, BinaryIO
from dotenv import load_dotenv

load_dotenv()

class SupabaseStorage:
    """Supabase Storage adapter for AI Agent"""
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_ANON_KEY')
        self.bucket_name = "ai-agent-files"
        self.client = None
        
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
            except ImportError:
                print("Supabase client not installed")
            except Exception as e:
                print(f"Supabase client initialization failed: {e}")
    
    def is_available(self) -> bool:
        """Check if Supabase storage is available"""
        return self.client is not None
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: str = "application/octet-stream") -> Optional[str]:
        """Upload file to Supabase storage"""
        if not self.is_available():
            return None
        
        try:
            result = self.client.storage.from_(self.bucket_name).upload(
                file_path,
                file_content,
                file_options={
                    "content-type": content_type,
                    "upsert": "true"
                }
            )
            
            if result:
                return f"supabase://{self.bucket_name}/{file_path}"
            return None
            
        except Exception as e:
            print(f"Supabase upload failed: {e}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file from Supabase storage"""
        if not self.is_available():
            return None
        
        try:
            # Remove supabase:// prefix if present
            if file_path.startswith("supabase://"):
                file_path = file_path.replace(f"supabase://{self.bucket_name}/", "")
            
            result = self.client.storage.from_(self.bucket_name).download(file_path)
            return result
            
        except Exception as e:
            print(f"Supabase download failed: {e}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file from Supabase storage"""
        if not self.is_available():
            return False
        
        try:
            # Remove supabase:// prefix if present
            if file_path.startswith("supabase://"):
                file_path = file_path.replace(f"supabase://{self.bucket_name}/", "")
            
            result = self.client.storage.from_(self.bucket_name).remove([file_path])
            return bool(result)
            
        except Exception as e:
            print(f"Supabase delete failed: {e}")
            return False
    
    def get_public_url(self, file_path: str) -> Optional[str]:
        """Get public URL for file (if bucket is public)"""
        if not self.is_available():
            return None
        
        try:
            # Remove supabase:// prefix if present
            if file_path.startswith("supabase://"):
                file_path = file_path.replace(f"supabase://{self.bucket_name}/", "")
            
            url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
            return url
            
        except Exception as e:
            print(f"Supabase public URL failed: {e}")
            return None

# Global instance
supabase_storage = SupabaseStorage()