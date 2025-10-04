#!/usr/bin/env python3
"""
Push all changes to git repository
"""
import subprocess
import os
import sys

def run_command(cmd, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Push all changes to git"""
    repo_path = os.path.dirname(os.path.abspath(__file__))
    
    print("Pushing changes to git repository...")
    print(f"Working directory: {repo_path}")
    
    # Check git status
    success, stdout, stderr = run_command("git status --porcelain", repo_path)
    if not success:
        print(f"Git status failed: {stderr}")
        return False
    
    if not stdout.strip():
        print("No changes to commit")
        return True
    
    print(f"Changes detected:\n{stdout}")
    
    # Add all changes
    print("Adding all changes...")
    success, stdout, stderr = run_command("git add .", repo_path)
    if not success:
        print(f"Git add failed: {stderr}")
        return False
    
    # Commit changes
    commit_message = "Fix upload route conflicts and add debugging tools - Fixed undefined variables in upload endpoints - Added debug logging for route conflicts - Created comprehensive upload testing tools - Enhanced CDN upload endpoint debugging - Added route enumeration and conflict detection"
    
    print("Committing changes...")
    success, stdout, stderr = run_command(f'git commit -m "{commit_message}"', repo_path)
    if not success:
        print(f"Git commit failed: {stderr}")
        return False
    
    # Push to remote
    print("Pushing to remote repository...")
    success, stdout, stderr = run_command("git push", repo_path)
    if not success:
        print(f"Git push failed: {stderr}")
        print("You may need to set up remote or authenticate")
        return False
    
    print("Successfully pushed all changes to git repository!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)