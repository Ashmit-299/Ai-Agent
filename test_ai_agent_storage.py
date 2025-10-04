#!/usr/bin/env python3
"""
Test AI Agent with Supabase Storage Integration
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_ai_agent_storage():
    """Test AI Agent storage integration"""
    
    print("Testing AI Agent with Supabase Storage...")
    
    # Test Supabase storage
    try:
        from core.supabase_storage import supabase_storage
        
        if supabase_storage.is_available():
            print("SUCCESS: Supabase storage available")
            
            # Test upload
            test_content = b"AI Agent storage integration test"
            file_path = "uploads/test-integration.txt"
            
            result = supabase_storage.upload_file(file_path, test_content, "text/plain")
            
            if result:
                print("SUCCESS: File uploaded to Supabase")
                print(f"File path: {result}")
                
                # Test download
                downloaded = supabase_storage.download_file(file_path)
                
                if downloaded == test_content:
                    print("SUCCESS: File downloaded and verified")
                    
                    # Cleanup
                    if supabase_storage.delete_file(file_path):
                        print("SUCCESS: File deleted")
                        
                        print("\n" + "="*50)
                        print("AI AGENT STORAGE INTEGRATION WORKING!")
                        print("="*50)
                        print("Storage: Supabase (1GB free)")
                        print("Upload: Working")
                        print("Download: Working")
                        print("Delete: Working")
                        print("Integration: Complete")
                        
                        return True
                    else:
                        print("ERROR: File delete failed")
                else:
                    print("ERROR: Downloaded content mismatch")
            else:
                print("ERROR: File upload failed")
        else:
            print("ERROR: Supabase storage not available")
            
    except ImportError as e:
        print(f"ERROR: Import failed - {e}")
    except Exception as e:
        print(f"ERROR: Integration test failed - {e}")
    
    return False

def test_server_startup():
    """Test if server can start"""
    
    print("\nTesting server startup...")
    
    try:
        from app.main import app
        print("SUCCESS: FastAPI app created")
        
        # Check if storage is configured
        use_supabase = os.getenv('USE_SUPABASE_STORAGE', 'false').lower() == 'true'
        use_s3 = os.getenv('USE_S3_STORAGE', 'false').lower() == 'true'
        
        print(f"Supabase storage: {'Enabled' if use_supabase else 'Disabled'}")
        print(f"S3 storage: {'Enabled' if use_s3 else 'Disabled'}")
        
        if use_supabase:
            print("SUCCESS: Server configured for Supabase storage")
            return True
        else:
            print("WARNING: No storage backend enabled")
            return False
            
    except Exception as e:
        print(f"ERROR: Server startup test failed - {e}")
        return False

if __name__ == "__main__":
    print("AI AGENT STORAGE INTEGRATION TEST")
    print("=" * 50)
    
    # Test storage integration
    storage_ok = test_ai_agent_storage()
    
    # Test server startup
    server_ok = test_server_startup()
    
    print("\n" + "="*50)
    if storage_ok and server_ok:
        print("ALL TESTS PASSED!")
        print("Your AI Agent is ready with Supabase storage")
        print("\nNext steps:")
        print("1. Start server: python scripts/start_server.py")
        print("2. Visit: http://localhost:9000")
        print("3. Upload files will now use Supabase storage")
    else:
        print("SOME TESTS FAILED")
        print("Check the errors above")
    print("="*50)