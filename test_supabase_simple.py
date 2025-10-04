#!/usr/bin/env python3
"""
Simple Supabase Storage Test
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_supabase_storage():
    """Test Supabase storage operations"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print("Testing Supabase Storage...")
    print(f"URL: {supabase_url}")
    
    if not supabase_url or not supabase_key:
        print("ERROR: Missing Supabase credentials")
        return False
    
    try:
        from supabase import create_client
        
        # Create client
        supabase = create_client(supabase_url, supabase_key)
        bucket_name = "ai-agent-files"
        
        print("Testing file upload...")
        
        # Test upload directly (skip bucket listing)
        test_content = b"Supabase storage test file"
        test_path = "test/upload-test.txt"
        
        try:
            # Upload test file
            upload_result = supabase.storage.from_(bucket_name).upload(
                test_path,
                test_content,
                file_options={"content-type": "text/plain", "upsert": "true"}
            )
            
            print("SUCCESS: File uploaded")
            
            # Test download
            print("Testing file download...")
            download_result = supabase.storage.from_(bucket_name).download(test_path)
            
            if download_result == test_content:
                print("SUCCESS: File downloaded and verified")
                
                # Test delete
                print("Testing file delete...")
                delete_result = supabase.storage.from_(bucket_name).remove([test_path])
                
                if delete_result:
                    print("SUCCESS: File deleted")
                    
                    print("\n" + "="*50)
                    print("SUPABASE STORAGE IS WORKING!")
                    print("="*50)
                    print("Bucket: ai-agent-files")
                    print("Upload: Working")
                    print("Download: Working")
                    print("Delete: Working")
                    print("Free Storage: 1GB available")
                    print("\nYour AI Agent can now use Supabase Storage!")
                    
                    return True
                else:
                    print("ERROR: File delete failed")
                    return False
            else:
                print("ERROR: Downloaded content doesn't match")
                return False
                
        except Exception as e:
            print(f"ERROR: File operations failed - {e}")
            
            # Check if it's a permissions issue
            if "policy" in str(e).lower() or "unauthorized" in str(e).lower():
                print("\nThis looks like a permissions issue.")
                print("Make sure your bucket policies allow:")
                print("- INSERT for uploads")
                print("- SELECT for downloads") 
                print("- DELETE for file removal")
                print("\nCheck your policies in Supabase dashboard.")
            
            return False
        
    except ImportError:
        print("ERROR: Supabase client not installed")
        print("Run: pip install supabase")
        return False
    except Exception as e:
        print(f"ERROR: Connection failed - {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_storage()
    
    if success:
        print("\nAll tests passed! Supabase storage is ready.")
    else:
        print("\nTests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("1. Bucket 'ai-agent-files' doesn't exist")
        print("2. Policies not configured correctly")
        print("3. Wrong Supabase credentials")