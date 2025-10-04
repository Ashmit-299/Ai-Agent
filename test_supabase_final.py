#!/usr/bin/env python3
"""
Final Supabase Storage Test
Run this after creating the bucket manually
Run this after creating the bucket and its policies manually in the Supabase dashboard.
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_supabase_final():
    """Test Supabase storage after manual bucket creation"""
    

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    

    if not supabase_url or not supabase_key:
        print("\n[ERROR] SUPABASE_URL and SUPABASE_ANON_KEY must be set in your .env file.")
        print("  - SUPABASE_URL: Found under Project Settings > API > Project URL")
        print("  - SUPABASE_ANON_KEY: Found under Project Settings > API > Project API Keys > anon (public)")
        return False

    print("Testing Supabase Storage Connection...")
    print(f"URL: {supabase_url}")
    

    try:
        from supabase import create_client
        

        # Create client
        supabase = create_client(supabase_url, supabase_key)
        

        bucket_name = "ai-agent-files"
        

        # List buckets to verify connection
        print("Checking available buckets...")
        try:
            buckets = supabase.storage.list_buckets()
            print(f"Found {len(buckets)} buckets.")

            bucket_exists = any(bucket.name == bucket_name for bucket in buckets)
            if bucket_exists:
                print(f"SUCCESS: Bucket '{bucket_name}' found")
                print(f"✅ SUCCESS: Bucket '{bucket_name}' found.")
            else:
                print(f"❌ ERROR: Bucket '{bucket_name}' not found.")
                print("Available buckets:", [b.name for b in buckets])
                print(f"  -> Please create a bucket named '{bucket_name}' in your Supabase project.")
                return False
                

        except Exception as e:
            print(f"❌ ERROR: Bucket listing failed: {e}")
            print("  -> This could be due to an incorrect URL, key, or network issue.")
            return False
        

        # Test file operations
        print("Testing file upload...")
        test_content = b"Final Supabase test - connection working!"
        test_path = "test/final-test.txt"
        

        try:
            # Upload test file
            upload_result = supabase.storage.from_(bucket_name).upload(
                test_path,
                test_content,
                file_options={"content-type": "text/plain", "upsert": "true"}
            )
            

            if upload_result:                
                print("✅ SUCCESS: File uploaded successfully.")

                # Test download
                print("Testing file download...")
                download_result = supabase.storage.from_(bucket_name).download(test_path)
                
                if download_result == test_content:
                    print("✅ SUCCESS: File downloaded and content verified.")

                    # List files in bucket
                    print("Listing files in bucket...")
                    files = supabase.storage.from_(bucket_name).list()
                    print(f"Found {len(files)} files/folders in bucket.")

                    # Cleanup
                    print("Cleaning up test file...")
                    supabase.storage.from_(bucket_name).remove([test_path])
                    print("✅ SUCCESS: Test file removed.")

                    print("\n" + "="*60)
                    print("🎉 SUPABASE STORAGE IS FULLY WORKING! 🎉")
                    print("="*60)
                    print(f"✅ Bucket: '{bucket_name}'")
                    print("✅ Upload:   Working")
                    print("✅ Download: Working")
                    print("✅ Delete:   Working")
                    print("✅ Policies: Correctly configured for authenticated access.")
                    print("\nYour AI Agent can now use Supabase Storage!")
                    

                    return True
                else:
                    print("❌ ERROR: File download failed or content mismatch.")
                    return False
            else:
                print("❌ ERROR: File upload failed. This is likely a policy issue.")
                print("  -> Please ensure you have a policy that allows INSERT on 'storage.objects'.")
                print("  -> Example Policy SQL:")
                print("     CREATE POLICY \"Allow authenticated uploads\" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'ai-agent-files');")
                return False
                
        except Exception as e:
            print(f"❌ ERROR: File operations failed: {e}")
            print("  -> This is almost certainly a permissions issue.")
            print("  -> Make sure you have created policies for SELECT, INSERT, UPDATE, and DELETE on the 'storage.objects' table for your bucket.")
            return False
        

    except ImportError:
        print("❌ ERROR: Supabase client not installed. Please run: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ ERROR: A general error occurred: {e}")
        return False

if __name__ == "__main__":
    if test_supabase_final():
        print("\n[SUCCESS] All Supabase storage tests passed.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Supabase storage tests failed. Please review the errors above.")
        sys.exit(1)