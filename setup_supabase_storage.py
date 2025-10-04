#!/usr/bin/env python3
"""
Setup Supabase Storage Bucket
"""
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def setup_supabase_storage():
    """Create storage bucket in Supabase"""
    try:
        from supabase import create_client
        
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Create storage bucket
        bucket_name = "ai-agent-files"
        
        # Try to create bucket (will fail if already exists)
        try:
            result = supabase.storage.create_bucket(bucket_name, {"public": True})
            print(f"Created storage bucket: {bucket_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"Storage bucket already exists: {bucket_name}")
            else:
                print(f"Failed to create bucket: {e}")
        
        # List existing buckets
        buckets = supabase.storage.list_buckets()
        print(f"Available buckets: {[b.name for b in buckets]}")
        
        return True
        
    except Exception as e:
        print(f"Supabase setup failed: {e}")
        return False

if __name__ == "__main__":
    print("Setting up Supabase storage...")
    setup_supabase_storage()