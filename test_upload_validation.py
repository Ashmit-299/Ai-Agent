#!/usr/bin/env python3
"""
Test upload endpoint and validate database saving
"""

import requests
import os
import time
from dotenv import load_dotenv
load_dotenv()

def test_upload_endpoint():
    """Test the upload endpoint and validate database saving"""
    
    print("Testing Upload Endpoint Validation")
    print("=" * 50)
    
    base_url = "http://localhost:9000"
    
    # Create a test file
    test_content = f"Test upload content - {time.time()}"
    test_filename = f"test_upload_{int(time.time())}.txt"
    
    with open(test_filename, 'w') as f:
        f.write(test_content)
    
    try:
        # Test upload
        print("1. Testing upload endpoint...")
        with open(test_filename, 'rb') as f:
            files = {'file': (test_filename, f, 'text/plain')}
            data = {
                'title': 'Test Upload Validation',
                'description': 'Testing if upload saves to database'
            }
            
            response = requests.post(f"{base_url}/upload", files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            print(f"   Upload Status: SUCCESS")
            print(f"   Content ID: {result.get('content_id')}")
            print(f"   Database Saved: {result.get('database_saved')}")
            print(f"   Bucket Saved: {result.get('bucket_saved')}")
            
            content_id = result.get('content_id')
            
            # Test if content appears in contents list
            print("\n2. Checking if content appears in database...")
            contents_response = requests.get(f"{base_url}/contents")
            
            if contents_response.status_code == 200:
                contents = contents_response.json()
                items = contents.get('items', [])
                
                # Look for our uploaded content
                found = False
                for item in items:
                    if item.get('content_id') == content_id:
                        found = True
                        print(f"   [OK] Content found in database!")
                        print(f"   Title: {item.get('title')}")
                        print(f"   Upload Time: {item.get('uploaded_at')}")
                        break
                
                if not found:
                    print(f"   [FAIL] Content NOT found in database")
                    print(f"   Total items in database: {len(items)}")
                    
            else:
                print(f"   [FAIL] Failed to check contents: {contents_response.status_code}")
            
            # Test direct database connection
            print("\n3. Testing direct database connection...")
            try:
                DATABASE_URL = os.getenv("DATABASE_URL")
                if DATABASE_URL and "postgresql" in DATABASE_URL:
                    import psycopg2
                    conn = psycopg2.connect(DATABASE_URL)
                    cur = conn.cursor()
                    
                    # Check if our content exists
                    cur.execute("SELECT content_id, title, uploaded_at FROM content WHERE content_id = %s", (content_id,))
                    row = cur.fetchone()
                    
                    if row:
                        print(f"   [OK] Content found in Supabase!")
                        print(f"   ID: {row[0]}")
                        print(f"   Title: {row[1]}")
                        print(f"   Uploaded: {row[2]}")
                    else:
                        print(f"   [FAIL] Content NOT found in Supabase")
                    
                    # Check total content count
                    cur.execute("SELECT COUNT(*) FROM content")
                    total = cur.fetchone()[0]
                    print(f"   Total content in Supabase: {total}")
                    
                    cur.close()
                    conn.close()
                else:
                    print(f"   [FAIL] No PostgreSQL DATABASE_URL configured")
                    
            except Exception as db_error:
                print(f"   [FAIL] Database connection failed: {db_error}")
            
        else:
            print(f"   Upload Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Test failed: {e}")
    
    finally:
        # Clean up test file
        try:
            os.remove(test_filename)
        except:
            pass
    
    print("\n" + "=" * 50)
    print("Upload validation test complete")

if __name__ == "__main__":
    test_upload_endpoint()