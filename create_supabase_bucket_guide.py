#!/usr/bin/env python3
"""
Step-by-Step Guide to Create Supabase Storage Bucket
"""
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

def open_supabase_dashboard():
    """Open Supabase dashboard in browser"""
    project_id = "dusqpdhojbgfxwflukhc"
    dashboard_url = f"https://supabase.com/dashboard/project/{project_id}"
    
    print("Opening Supabase Dashboard...")
    print(f"URL: {dashboard_url}")
    
    try:
        webbrowser.open(dashboard_url)
        print("✅ Dashboard opened in browser")
    except:
        print("❌ Could not open browser automatically")
        print(f"Please manually visit: {dashboard_url}")

def show_bucket_creation_steps():
    """Show detailed steps to create bucket"""
    
    print("\n" + "="*60)
    print("📋 SUPABASE STORAGE BUCKET CREATION GUIDE")
    print("="*60)
    
    print("\n🔗 STEP 1: Open Supabase Dashboard")
    print("   Visit: https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc")
    print("   (Opening automatically...)")
    
    print("\n📁 STEP 2: Navigate to Storage")
    print("   1. Look for 'Storage' in the left sidebar")
    print("   2. Click on 'Storage'")
    print("   3. You should see 'Create a new bucket' button")
    
    print("\n🆕 STEP 3: Create New Bucket")
    print("   1. Click 'Create a new bucket'")
    print("   2. Bucket name: ai-agent-files")
    print("   3. Public bucket: UNCHECK (keep it private)")
    print("   4. Click 'Create bucket'")
    
    print("\n🔐 STEP 4: Set Bucket Policies")
    print("   1. Click on your new 'ai-agent-files' bucket")
    print("   2. Go to 'Policies' tab")
    print("   3. Click 'New Policy'")
    print("   4. Choose 'For full customization'")
    print("   5. Policy name: Allow all operations")
    print("   6. Copy and paste this SQL:")
    
    print("\n📝 SQL POLICY CODE:")
    print("-" * 40)
    sql_policy = """CREATE POLICY "Allow all operations" ON storage.objects
FOR ALL USING (bucket_id = 'ai-agent-files');"""
    print(sql_policy)
    print("-" * 40)
    
    print("\n   7. Click 'Review'")
    print("   8. Click 'Save policy'")
    
    print("\n✅ STEP 5: Test Connection")
    print("   Run: python test_supabase_final.py")
    
    print("\n" + "="*60)
    print("🚨 IMPORTANT NOTES:")
    print("- Bucket name must be exactly: ai-agent-files")
    print("- Keep bucket PRIVATE (not public)")
    print("- The policy is required for file operations")
    print("- If you get errors, double-check the policy SQL")
    print("="*60)

def check_current_setup():
    """Check current environment setup"""
    
    print("\n🔍 CHECKING CURRENT SETUP:")
    print("-" * 30)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    print(f"SUPABASE_URL: {'✅ Set' if supabase_url else '❌ Missing'}")
    print(f"SUPABASE_ANON_KEY: {'✅ Set' if supabase_key else '❌ Missing'}")
    
    if supabase_url:
        print(f"Project URL: {supabase_url}")
    
    if not supabase_url or not supabase_key:
        print("\n❌ Environment variables missing!")
        print("Make sure your .env file has:")
        print("SUPABASE_URL=https://dusqpdhojbgfxwflukhc.supabase.co")
        print("SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 SUPABASE STORAGE SETUP HELPER")
    
    # Check environment
    if not check_current_setup():
        exit(1)
    
    # Show steps
    show_bucket_creation_steps()
    
    # Open dashboard
    input("\nPress Enter to open Supabase Dashboard...")
    open_supabase_dashboard()
    
    print("\n⏳ After creating the bucket and policy:")
    print("Run: python test_supabase_final.py")
    print("\nNeed help? The bucket creation steps are shown above.")