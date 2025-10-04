#!/usr/bin/env python3
"""
Correct Supabase Storage Policies
"""

def show_correct_policies():
    """Show the correct policy format"""
    
    print("CORRECT SUPABASE STORAGE POLICIES")
    print("=" * 50)
    
    print("\nSTEP 1: Delete all existing policies")
    print("Go to Storage > ai-agent-files > Policies")
    print("Delete all current policies")
    
    print("\nSTEP 2: Create 4 separate policies")
    print("Create each policy individually:")
    
    print("\n1. POLICY FOR INSERT (Upload)")
    print("Name: Allow INSERT")
    print("Command: INSERT")
    print("Target roles: anon")
    print("SQL:")
    print("CREATE POLICY \"Allow INSERT\" ON storage.objects")
    print("FOR INSERT TO anon")
    print("WITH CHECK (bucket_id = 'ai-agent-files');")
    
    print("\n2. POLICY FOR SELECT (Download)")
    print("Name: Allow SELECT")
    print("Command: SELECT")
    print("Target roles: anon")
    print("SQL:")
    print("CREATE POLICY \"Allow SELECT\" ON storage.objects")
    print("FOR SELECT TO anon")
    print("USING (bucket_id = 'ai-agent-files');")
    
    print("\n3. POLICY FOR UPDATE")
    print("Name: Allow UPDATE")
    print("Command: UPDATE")
    print("Target roles: anon")
    print("SQL:")
    print("CREATE POLICY \"Allow UPDATE\" ON storage.objects")
    print("FOR UPDATE TO anon")
    print("USING (bucket_id = 'ai-agent-files')")
    print("WITH CHECK (bucket_id = 'ai-agent-files');")
    
    print("\n4. POLICY FOR DELETE")
    print("Name: Allow DELETE")
    print("Command: DELETE")
    print("Target roles: anon")
    print("SQL:")
    print("CREATE POLICY \"Allow DELETE\" ON storage.objects")
    print("FOR DELETE TO anon")
    print("USING (bucket_id = 'ai-agent-files');")
    
    print("\nSTEP 3: Test")
    print("Run: python test_supabase_simple.py")
    
    print("\n" + "=" * 50)
    print("ALTERNATIVE: Single policy for all operations")
    print("If individual policies don't work, try this:")
    print("Name: Allow all operations")
    print("Command: ALL")
    print("Target roles: anon")
    print("SQL:")
    print("CREATE POLICY \"Allow all operations\" ON storage.objects")
    print("FOR ALL TO anon")
    print("USING (bucket_id = 'ai-agent-files')")
    print("WITH CHECK (bucket_id = 'ai-agent-files');")

if __name__ == "__main__":
    show_correct_policies()