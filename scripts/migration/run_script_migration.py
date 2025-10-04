#!/usr/bin/env python3
"""
Run the script table migration
"""
import os
import sys
import subprocess

def run_migration():
    """Run the script table migration"""
    try:
        print("🔄 Running script table migration...")
        
        # Run the specific migration
        result = subprocess.run(['alembic', 'upgrade', '004'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Script table migration completed successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Migration failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Migration execution failed: {e}")
        return False

if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)