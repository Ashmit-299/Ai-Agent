#!/usr/bin/env python3
"""
Migration check script for CI/CD pipeline
"""
import os
import sys
import subprocess
from pathlib import Path

def check_migrations():
    """Check if migrations are ready to apply"""
    try:
        # Check if alembic is available
        result = subprocess.run(['alembic', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Alembic not installed")
            return False
        
        print(f"✅ Alembic version: {result.stdout.strip()}")
        
        # Check migration files exist
        migrations_dir = Path("migrations/versions")
        if not migrations_dir.exists():
            print("❌ Migrations directory not found")
            return False
        
        migration_files = list(migrations_dir.glob("*.py"))
        if len(migration_files) == 0:
            print("❌ No migration files found")
            return False
        
        print(f"✅ Found {len(migration_files)} migration files")
        
        # Check current database revision
        result = subprocess.run(['alembic', 'current'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Cannot check current revision: {result.stderr}")
            return False
        
        current_revision = result.stdout.strip()
        print(f"✅ Current revision: {current_revision}")
        
        # Check pending migrations
        result = subprocess.run(['alembic', 'check'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"⚠️ Pending migrations detected: {result.stderr}")
            print("This is normal for new deployments")
        else:
            print("✅ Database is up to date")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration check failed: {e}")
        return False

if __name__ == "__main__":
    success = check_migrations()
    sys.exit(0 if success else 1)