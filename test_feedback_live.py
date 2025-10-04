#!/usr/bin/env python3
"""
Test feedback endpoint with detailed error logging
"""
import requests
import json
import traceback

def test_feedback_endpoint():
    """Test the feedback endpoint and capture detailed errors"""
    
    # Test data
    url = "http://localhost:9000/feedback"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhc2htIiwidXNlcl9pZCI6IjU0NDk1MTY4NjBmOSIsImV4cCI6MTc1OTY1NDE1NCwiaWF0IjoxNzU5NTY3NzU0LCJ0eXBlIjoiYWNjZXNzIiwianRpIjoiSWk5b0lsY2dzbllRdjRnUG03eU1VUSJ9.Iyi2mpL-kOtUTc8ExWRsDFd_4PV-I21jZIEFwcKqW24"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    data = {
        "content_id": "9a2b35e14d7c_30df5d",
        "rating": 5,
        "comment": "great"
    }
    
    print("Testing feedback endpoint...")
    print(f"URL: {url}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("\nSending request...")
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"\nResponse Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2))
        except:
            print(response.text)
        
        if response.status_code == 500:
            print("\n" + "="*60)
            print("ERROR DETECTED - Checking possible causes...")
            print("="*60)
            
            # Check if agent.py exists and is working
            print("\n1. Checking RL Agent...")
            try:
                from app.agent import RLAgent
                agent = RLAgent(state_path='agent_state.json')
                print("   [OK] RL Agent initialized")
            except Exception as e:
                print(f"   [ERROR] RL Agent failed: {e}")
            
            # Check database connection
            print("\n2. Checking database...")
            try:
                import os
                from dotenv import load_dotenv
                load_dotenv()
                
                import psycopg2
                DATABASE_URL = os.getenv("DATABASE_URL")
                conn = psycopg2.connect(DATABASE_URL)
                cur = conn.cursor()
                
                # Check if content exists
                cur.execute("SELECT content_id, title FROM content WHERE content_id = %s", (data['content_id'],))
                content = cur.fetchone()
                
                if content:
                    print(f"   [OK] Content found: {content[1]}")
                else:
                    print(f"   [ERROR] Content not found: {data['content_id']}")
                
                cur.close()
                conn.close()
            except Exception as e:
                print(f"   [ERROR] Database check failed: {e}")
            
            # Check observability imports
            print("\n3. Checking observability...")
            try:
                from app.observability import set_user_context, track_event
                print("   [OK] Observability imports working")
            except Exception as e:
                print(f"   [ERROR] Observability failed: {e}")
            
            # Check save_json function
            print("\n4. Checking storage functions...")
            try:
                from core.s3_storage_adapter import save_json
                print("   [OK] save_json available")
            except:
                try:
                    from core.bhiv_bucket import save_json
                    print("   [OK] save_json available (bhiv_bucket)")
                except Exception as e:
                    print(f"   [ERROR] save_json not available: {e}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n[ERROR] Request failed: {e}")
        print(traceback.format_exc())
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_feedback_endpoint()
