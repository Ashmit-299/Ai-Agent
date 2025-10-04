#!/usr/bin/env python3
"""
Fix Supabase Storage Policies
The current policies are for 'authenticated' users, but we're using anon key
"""

def show_correct_policies():
    """Show the correct policies for anon key access"""
    
    print("SUPABASE STORAGE POLICY FIX")
    print("=" * 50)
    
    print("\nPROBLEM:")
    print("Your current policies are for 'authenticated' users")
    print("But you're using the anon (public) key")
    
    print("\nSOLUTION:")
    print("Replace your current policies with these:")
    
    print("\n1. DELETE ALL EXISTING POLICIES")
    print("   - Go to Storage > ai-agent-files > Policies")
    print("   - Delete all 4 existing policies")
    
    print("\n2. CREATE ONE NEW POLICY")
    print("   - Click 'New Policy'")
    print("   - Choose 'For full customization'")
    print("   - Policy name: Allow anon access")
    print("   - Target roles: Leave empty or select 'anon'")
    print("   - Paste this SQL:")
    
    print("\nCORRECT SQL POLICY:")
    print("-" * 40)
    sql_policy = """CREATE POLICY "Allow anon access" ON storage.objects
FOR ALL TO anon
USING (bucket_id = 'ai-agent-files')
WITH CHECK (bucket_id = 'ai-agent-files');"""
    print(sql_policy)
    print("-" * 40)
    
    print("\n3. SAVE THE POLICY")
    print("   - Click 'Review'")
    print("   - Click 'Save policy'")
    
    print("\n4. TEST AGAIN")
    print("   Run: python test_supabase_simple.py")
    
    print("\nALTERNATIVE APPROACH:")
    print("If the above doesn't work, try this simpler policy:")
    print("-" * 40)
    simple_policy = """CREATE POLICY "Allow all access" ON storage.objects
FOR ALL
USING (true);"""
    print(simple_policy)
    print("-" * 40)
    print("(This allows all access - less secure but will work)")
    
    print("\n" + "=" * 50)

def show_step_by_step():
    """Show detailed steps"""
    
    print("\nSTEP-BY-STEP POLICY FIX:")
    print("1. Go to: https://supabase.com/dashboard/project/dusqpdhojbgfxwflukhc")
    print("2. Click 'Storage' in sidebar")
    print("3. Click 'ai-agent-files' bucket")
    print("4. Click 'Policies' tab")
    print("5. Delete all existing policies (click trash icon)")
    print("6. Click 'New Policy'")
    print("7. Choose 'For full customization'")
    print("8. Policy name: Allow anon access")
    print("9. Paste the SQL from above")
    print("10. Click 'Review' then 'Save policy'")
    print("11. Test with: python test_supabase_simple.py")

if __name__ == "__main__":
    show_correct_policies()
    show_step_by_step()
    
    print("\nAfter fixing policies, run:")
    print("python test_supabase_simple.py")