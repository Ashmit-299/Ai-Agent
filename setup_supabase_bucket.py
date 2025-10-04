#!/usr/bin/env python3
"""
Setup Supabase Storage Bucket
"""
import os
from dotenv import load_dotenv

load_dotenv()

def setup_supabase_bucket():
    """Setup Supabase Storage Bucket"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("Setting up Supabase Storage...")
    print(f"URL: {supabase_url}")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Supabase credentials missing")
        return False
    
    try:
        from supabase import create_client
        
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        
        # Bucket name
        bucket_name = "ai-agent-files"
        
        print(f"Creating bucket: {bucket_name}")
        
        try:
            # Create bucket with proper options
            result = supabase.storage.create_bucket(
                bucket_name,
                options={"public": False}
            )
            print("SUCCESS: Bucket created")
        except Exception as e:
            error_msg = str(e).lower()
            if "already exists" in error_msg or "duplicate" in error_msg:
                print("SUCCESS: Bucket already exists")
            else:
                print(f"Bucket creation issue: {e}")
                # Continue anyway - bucket might exist
        
        # Test upload
        print("Testing file upload...")
        test_content = b"Supabase storage connection test"
        test_path = "test/connection-test.txt"
        
        try:
            upload_result = supabase.storage.from_(bucket_name).upload(
                test_path,
                test_content,
                file_options={"content-type": "text/plain"}
            )
            print("SUCCESS: File uploaded")
            
            # Test download
            print("Testing file download...")
            download_result = supabase.storage.from_(bucket_name).download(test_path)
            
            if download_result:
                print("SUCCESS: File downloaded")
                
                # Get public URL (for testing)
                try:
                    public_url = supabase.storage.from_(bucket_name).get_public_url(test_path)
                    print(f"File URL: {public_url}")
                except:
                    pass  # Public URLs might not work for private buckets
                
                # Cleanup
                print("Cleaning up test file...")
                supabase.storage.from_(bucket_name).remove([test_path])
                print("SUCCESS: Cleanup completed")
                
                print("\n" + "="*50)
                print("SUPABASE STORAGE IS READY!")
                print("="*50)
                print("Bucket name: ai-agent-files")
                print("Storage: 1GB free")
                print("Status: Connected and working")
                
                return True
            else:
                print("ERROR: Download failed")
                return False
                
        except Exception as e:
            print(f"Upload/Download test failed: {e}")
            return False
        
    except ImportError:
        print("ERROR: Supabase client not installed")
        print("Run: pip install supabase")
        return False
    except Exception as e:
        print(f"ERROR: Setup failed - {e}")
        return False

def create_bucket_manually():
    """Instructions to create bucket manually"""
    
    print("\nMANUAL BUCKET CREATION:")
    print("="*40)
    print("1. Go to: https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc")
    print("2. Click 'Storage' in left sidebar")
    print("3. Click 'Create a new bucket'")
    print("4. Bucket name: ai-agent-files")
    print("5. Make it Private (uncheck Public)")
    print("6. Click 'Create bucket'")
    print("7. Run this script again")

if __name__ == "__main__":
    success = setup_supabase_bucket()
    
    if not success:
        create_bucket_manually()