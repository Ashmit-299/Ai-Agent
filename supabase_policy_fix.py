#!/usr/bin/env python3
"""
Correct Supabase Policy Format - No CREATE POLICY needed
"""

def show_dashboard_format():
    """Show the correct format for Supabase dashboard"""
    
    print("SUPABASE POLICY FIX - Dashboard Format")
    print("=" * 50)
    
    print("\nERROR CAUSE:")
    print("Don't include 'CREATE POLICY' in the dashboard")
    print("The dashboard adds that automatically")
    
    print("\nCORRECT STEPS:")
    print("1. Go to Storage > ai-agent-files > Policies")
    print("2. Delete all existing policies")
    print("3. Click 'New Policy'")
    print("4. Choose 'For full customization'")
    
    print("\nPOLICY SETTINGS:")
    print("Policy name: Allow all operations")
    print("Target roles: anon")
    print("Policy command: ALL")
    
    print("\nPOLICY DEFINITION (paste this only):")
    print("-" * 40)
    print("bucket_id = 'ai-agent-files'")
    print("-" * 40)
    
    print("\nOR try this simpler approach:")
    print("Policy definition:")
    print("-" * 40)
    print("true")
    print("-" * 40)
    print("(This allows all access)")
    
    print("\nSTEPS IN DETAIL:")
    print("1. Policy name: Allow all operations")
    print("2. Target roles: Select 'anon'")
    print("3. Policy command: Select 'ALL'")
    print("4. Policy definition: bucket_id = 'ai-agent-files'")
    print("5. Click 'Review' then 'Save policy'")
    
    print("\nIF THAT DOESN'T WORK:")
    print("Try the simplest policy:")
    print("Policy definition: true")
    print("(This allows everything - less secure but will work)")

if __name__ == "__main__":
    show_dashboard_format()