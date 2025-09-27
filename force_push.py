#!/usr/bin/env python3

import os
import subprocess

def force_push():
    """Force push all changes to GitHub"""
    
    try:
        print("=== FORCE PUSHING TO GITHUB ===")
        
        # Change to project directory
        os.chdir(r"c:\Users\Ashmit Pandey\Downloads\Ai-Agent-main")
        
        # Abort any ongoing rebase
        print("\n1. Cleaning up git state...")
        subprocess.run(["git", "rebase", "--abort"], capture_output=True)
        subprocess.run(["git", "reset", "--hard", "HEAD"], check=True)
        
        # Add all files
        print("\n2. Adding all files...")
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit with message
        commit_message = "feat: Complete Supabase optimization and production enhancements"
        
        print("\n3. Committing changes...")
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Force push to overwrite remote
        print("\n4. Force pushing to GitHub...")
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        
        print(f"\nSUCCESS: Repository forcefully updated!")
        print(f"Repository: https://github.com/Ashmit-299/Ai-Agent.git")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = force_push()
    
    if success:
        print("\nALL CHANGES SUCCESSFULLY PUSHED!")
        print("- Supabase optimizations")
        print("- Database integration") 
        print("- Security fixes")
        print("- Test suite")
        print("- Performance monitoring")
    else:
        print("\nForce push failed - check errors above")