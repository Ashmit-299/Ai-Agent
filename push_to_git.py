#!/usr/bin/env python3

import os
import subprocess

def push_to_git():
    """Push all changes to GitHub repository"""
    
    try:
        print("=== PUSHING TO GITHUB REPOSITORY ===")
        
        # Change to project directory
        os.chdir(r"c:\Users\Ashmit Pandey\Downloads\Ai-Agent-main")
        
        # Check git status
        print("\n1. Checking git status...")
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout:
            print(f"Found {len(result.stdout.splitlines())} changed files")
        else:
            print("No changes detected")
            return True
        
        # Add all changes
        print("\n2. Adding all changes...")
        subprocess.run(["git", "add", "."], check=True)
        print("All files added to staging")
        
        # Create comprehensive commit message
        commit_message = """feat: Complete Supabase optimization and database integration

- Fixed all Supabase Performance Advisor warnings
- Optimized 11 RLS policies for auth performance  
- Removed 34+ unused and duplicate indexes
- Created 6 essential foreign key indexes
- Added comprehensive database integration module
- Enhanced analytics endpoints and tracking
- Fixed CWE-798 hardcoded credentials issues
- Added complete API test suite
- Updated CI/CD pipeline error handling
- Integrated PostHog and Sentry observability

Database optimizations:
- Auth functions now evaluate once per query vs per row
- No duplicate indexes remaining
- All foreign keys properly indexed
- Table statistics updated for query optimization
- Production-ready performance improvements

New features:
- Enhanced analytics table with comprehensive tracking
- Complete Supabase table integration (7 tables)
- Fallback database systems for reliability
- Comprehensive test coverage for all endpoints
- Performance monitoring and health checks"""

        # Commit changes
        print("\n3. Committing changes...")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("Changes committed successfully")
        
        # Push to origin
        print("\n4. Pushing to GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Successfully pushed to GitHub!")
        
        # Show final status
        print("\n5. Final repository status:")
        subprocess.run(["git", "log", "--oneline", "-5"], check=True)
        
        print(f"\nSUCCESS: All changes pushed to:")
        print(f"https://github.com/Ashmit-299/Ai-Agent.git")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        print(f"Command: {e.cmd}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = push_to_git()
    
    if success:
        print("\nRepository successfully updated with all optimizations!")
        print("- Supabase performance fixes")
        print("- Database integration enhancements") 
        print("- Security improvements")
        print("- Complete test suite")
        print("- CI/CD pipeline updates")
    else:
        print("\nFailed to push to repository. Check errors above.")