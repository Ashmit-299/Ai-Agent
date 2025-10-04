#!/usr/bin/env python3
"""
Test Free Storage Options
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_supabase_storage():
    """Test Supabase Storage (Free 1GB)"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("Testing Supabase Storage...")
    print(f"URL: {supabase_url}")
    print(f"Key: {'Set' if supabase_key else 'Missing'}")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Supabase credentials missing in .env")
        return False
    
    try:
        from supabase import create_client
        
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        
        # Create bucket
        bucket_name = "ai-agent-files"
        
        try:
            result = supabase.storage.create_bucket(bucket_name, {"public": False})
            print(f"SUCCESS: Created bucket {bucket_name}")
        except Exception as e:
            if "already exists" in str(e).lower():
                print(f"SUCCESS: Bucket {bucket_name} already exists")
            else:
                print(f"ERROR: Bucket creation failed - {e}")
                return False
        
        # Test upload
        test_content = b"Supabase storage test"
        test_path = "test/connection-test.txt"
        
        upload_result = supabase.storage.from_(bucket_name).upload(
            test_path, 
            test_content,
            {"content-type": "text/plain"}
        )
        
        if upload_result:
            print("SUCCESS: Upload test passed")
            
            # Test download
            download_result = supabase.storage.from_(bucket_name).download(test_path)
            if download_result:
                print("SUCCESS: Download test passed")
                
                # Cleanup
                supabase.storage.from_(bucket_name).remove([test_path])
                print("SUCCESS: Cleanup completed")
                
                print("\nSUPABASE STORAGE READY!")
                print("Add to .env:")
                print("USE_SUPABASE_STORAGE=true")
                return True
        
        return False
        
    except ImportError:
        print("ERROR: Supabase client not installed")
        print("Run: pip install supabase")
        return False
    except Exception as e:
        print(f"ERROR: Supabase storage test failed - {e}")
        return False

def show_free_options():
    """Show all free storage options"""
    
    print("FREE STORAGE OPTIONS:")
    print("=" * 40)
    
    print("\n1. SUPABASE STORAGE (Recommended)")
    print("   - Free: 1GB storage")
    print("   - You already have account")
    print("   - Setup: 2 minutes")
    print("   - Test: python test_free_storage.py")
    
    print("\n2. CLOUDFLARE R2")
    print("   - Free: 10GB storage")
    print("   - S3-compatible")
    print("   - Setup: cloudflare.com/developer-platform/r2/")
    
    print("\n3. MINIO (Self-hosted)")
    print("   - Free: Unlimited")
    print("   - Runs on your computer")
    print("   - Setup: python setup_minio.py start")
    
    print("\n4. BACKBLAZE B2")
    print("   - Free: 10GB storage")
    print("   - Setup: backblaze.com/b2/")
    
    print("\n5. KEEP LOCAL STORAGE")
    print("   - Free: Unlimited")
    print("   - Already working")
    print("   - No setup needed")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'supabase':
        test_supabase_storage()
    else:
        show_free_options()
        
        print("\nTo test Supabase Storage:")
        print("python test_free_storage.py supabase")