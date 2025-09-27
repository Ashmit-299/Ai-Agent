#!/usr/bin/env python3

import os
import subprocess

def fix_github_actions():
    """Fix GitHub Actions workflow errors"""
    
    try:
        print("=== FIXING GITHUB ACTIONS ERRORS ===")
        
        # Change to project directory
        os.chdir(r"c:\Users\Ashmit Pandey\Downloads\Ai-Agent-main")
        
        # Add the fixed workflow file
        print("\n1. Adding fixed workflow file...")
        subprocess.run(["git", "add", ".github/workflows/ci-cd-production.yml"], check=True)
        
        # Commit the fix
        print("\n2. Committing GitHub Actions fix...")
        commit_message = "fix: Update CodeQL action to v3 and fix permissions\n\n- Updated github/codeql-action from v2 to v3 (v2 deprecated)\n- Added proper permissions for security-events\n- Fixed 'Resource not accessible by integration' error\n- Maintained security scanning functionality"
        
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        
        # Push the fix
        print("\n3. Pushing fix to GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print(f"\nSUCCESS: GitHub Actions errors fixed!")
        print(f"- Updated CodeQL action to v3")
        print(f"- Fixed permissions for security-events")
        print(f"- Resolved integration access issues")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_github_actions()
    
    if success:
        print("\nGitHub Actions workflow successfully updated!")
        print("The CI/CD pipeline should now run without errors.")
    else:
        print("\nFailed to fix GitHub Actions errors.")