#!/usr/bin/env python3
"""
Test Root Endpoint Display
"""
import requests
import webbrowser
import time

def test_root_endpoint():
    """Test the root endpoint and save HTML for inspection"""
    
    try:
        print("Testing root endpoint...")
        response = requests.get('http://127.0.0.1:9000/', timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)} characters")
        print(f"Content Type: {response.headers.get('content-type', 'unknown')}")
        
        if response.status_code == 200:
            # Save HTML to file for inspection
            with open('root_response.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print("HTML saved to root_response.html")
            print("\nFirst 300 characters:")
            print(response.text[:300])
            
            # Check if it contains expected content
            if "AI Content Uploader Agent" in response.text:
                print("\n✅ SUCCESS: HTML contains expected title")
            else:
                print("\n❌ ERROR: HTML missing expected title")
            
            if "Server Running Successfully" in response.text:
                print("✅ SUCCESS: HTML contains status message")
            else:
                print("❌ ERROR: HTML missing status message")
            
            if "/docs" in response.text:
                print("✅ SUCCESS: HTML contains navigation links")
            else:
                print("❌ ERROR: HTML missing navigation links")
            
            # Try to open in browser
            try:
                webbrowser.open('http://127.0.0.1:9000/')
                print("\n🌐 Browser opened to test visual display")
            except:
                print("\n⚠️ Could not open browser automatically")
            
            return True
        else:
            print(f"❌ ERROR: Unexpected status code {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server")
        print("Make sure server is running on http://127.0.0.1:9000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_other_endpoints():
    """Test other key endpoints"""
    
    endpoints = [
        ('/health', 'Health Check'),
        ('/docs', 'API Documentation'),
        ('/test', 'Test Endpoint')
    ]
    
    print("\nTesting other endpoints...")
    
    for path, name in endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:9000{path}', timeout=5)
            status = "✅ OK" if response.status_code == 200 else f"❌ {response.status_code}"
            print(f"{name}: {status}")
        except Exception as e:
            print(f"{name}: ❌ ERROR - {e}")

if __name__ == "__main__":
    print("ROOT ENDPOINT DISPLAY TEST")
    print("=" * 40)
    
    success = test_root_endpoint()
    test_other_endpoints()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Root endpoint is working!")
        print("If you still see a white screen:")
        print("1. Check browser console for JavaScript errors")
        print("2. Try hard refresh (Ctrl+F5)")
        print("3. Try different browser")
        print("4. Check root_response.html file")
    else:
        print("❌ Root endpoint has issues")
    
    print("\nServer URL: http://127.0.0.1:9000")
    print("API Docs: http://127.0.0.1:9000/docs")