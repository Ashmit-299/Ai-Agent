#!/usr/bin/env python3
"""
Manual Supabase Bucket Setup Guide
"""
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

def show_setup_guide():
    """Show step-by-step setup guide"""
    
    print("SUPABASE STORAGE SETUP GUIDE")
    print("=" * 50)
    
    print("\nSTEP 1: Open Supabase Dashboard")
    print("URL: https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc")
    
    print("\nSTEP 2: Navigate to Storage")
    print("- Click 'Storage' in left sidebar")
    print("- Click 'Create a new bucket'")
    
    print("\nSTEP 3: Create Bucket")
    print("- Bucket name: ai-agent-files")
    print("- Public bucket: UNCHECK (keep private)")
    print("- Click 'Create bucket'")
    
    print("\nSTEP 4: Create Policy")
    print("- Click on 'ai-agent-files' bucket")
    print("- Go to 'Policies' tab")
    print("- Click 'New Policy'")
    print("- Choose 'For full customization'")
    print("- Policy name: Allow all operations")
    print("- Paste this SQL:")
    
    print("\nSQL POLICY:")
    print("-" * 40)
    print("CREATE POLICY \"Allow all operations\" ON storage.objects")
    print("FOR ALL USING (bucket_id = 'ai-agent-files');")
    print("-" * 40)
    
    print("\n- Click 'Review' then 'Save policy'")
    
    print("\nSTEP 5: Test")
    print("Run: python test_supabase_final.py")
    
    print("\n" + "=" * 50)

def open_dashboard():
    """Open Supabase dashboard"""
    url = "https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc"
    try:
        webbrowser.open(url)
        print("Dashboard opened in browser")
    except:
        print(f"Please visit: {url}")

if __name__ == "__main__":
    show_setup_guide()
    
    input("\nPress Enter to open dashboard...")
    open_dashboard()
    
    print("\nAfter setup, run: python test_supabase_final.py")