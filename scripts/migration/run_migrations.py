#!/usr/bin/env python3
"""
Production-ready migration runner with enhanced error handling
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def run_alembic_command(cmd_args):
    """Run Alembic command using Python module"""
    try:
        from alembic.config import main as alembic_main
        import sys
        
        # Save original argv
        original_argv = sys.argv
        
        # Set argv for alembic
        sys.argv = ['alembic'] + cmd_args
        
        try:
            alembic_main()
            print(f"[SUCCESS] alembic {' '.join(cmd_args)}")
            return True
        except SystemExit as e:
            if e.code == 0:
                print(f"[SUCCESS] alembic {' '.join(cmd_args)}")
                return True
            else:
                print(f"[ERROR] alembic {' '.join(cmd_args)} - Exit code: {e.code}")
                return False
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except ImportError:
        print("[ERROR] Alembic not installed. Run: pip install alembic")
        return False
    except Exception as e:
        print(f"[ERROR] Alembic command failed: {e}")
        return False

def init_migrations():
    """Initialize database with all tables"""
    print("[INFO] Initializing database...")
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Create tables using SQLModel
    try:
        from core.models import create_db_and_tables
        create_db_and_tables()
        print("[SUCCESS] Database tables created")
        print("[INFO] Database initialization complete")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}")
        return False

def upgrade_migrations():
    """Run database migrations"""
    print("[INFO] Running migrations...")
    return run_alembic_command(["upgrade", "head"])

def create_migration(message):
    """Create new migration"""
    print(f"[INFO] Creating migration: {message}")
    return run_alembic_command(["revision", "--autogenerate", "-m", message])

def main():
    """Main migration runner"""
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py [init|upgrade|create <message>]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        success = init_migrations()
    elif command == "upgrade":
        success = upgrade_migrations()
    elif command == "create" and len(sys.argv) > 2:
        message = " ".join(sys.argv[2:])
        success = create_migration(message)
    else:
        print("Invalid command")
        sys.exit(1)
    
    if success:
        print("[SUCCESS] Migration completed successfully")
    else:
        print("[ERROR] Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()