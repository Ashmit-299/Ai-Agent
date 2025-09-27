#!/usr/bin/env python3
"""
Run complete test suite with migration
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"⚠️ {description} had issues:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

def main():
    print("🚀 AI Agent Complete Test Suite Runner")
    print("=" * 50)
    
    # Step 1: Run migration
    if run_command("python scripts/migration/run_migrations.py upgrade", "Running database migrations"):
        print("✅ Database is ready")
    else:
        print("⚠️ Migration had issues, continuing anyway...")
    
    # Step 2: Run the complete test
    print("\n🧪 Starting API test suite...")
    run_command("python test_all_endpoints.py", "Running complete API tests")
    
    print("\n🎯 Test suite completed!")
    print("Check your Supabase database for all the generated test data.")

if __name__ == "__main__":
    main()