#!/usr/bin/env python3
"""
Database Migration Runner
Runs Alembic migrations for Supabase database
"""

import os
import sys
from dotenv import load_dotenv
from alembic.config import Config
from alembic import command
import logging

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for migration process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable not set")
    return db_url

def run_migrations(command_type="upgrade"):
    """Run database migrations"""
    logger = setup_logging()
    
    try:
        # Verify database URL
        db_url = get_database_url()
        logger.info(f"Using database: {db_url[:50]}...")
        
        # Setup Alembic configuration
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        logger.info(f"Running migration command: {command_type}")
        
        if command_type == "upgrade":
            # Run all pending migrations
            command.upgrade(alembic_cfg, "head")
            logger.info("SUCCESS: All migrations completed successfully")
            
        elif command_type == "current":
            # Show current revision
            command.current(alembic_cfg)
            
        elif command_type == "history":
            # Show migration history
            command.history(alembic_cfg)
            
        elif command_type == "downgrade":
            # Downgrade one revision
            command.downgrade(alembic_cfg, "-1")
            logger.info("SUCCESS: Downgrade completed")
            
        else:
            logger.error(f"Unknown command: {command_type}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

def check_migration_status():
    """Check current migration status"""
    logger = setup_logging()
    
    try:
        db_url = get_database_url()
        alembic_cfg = Config("alembic.ini")
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        
        logger.info("Current migration status:")
        command.current(alembic_cfg, verbose=True)
        
        logger.info("\nMigration history:")
        command.history(alembic_cfg)
        
        return True
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return False

def main():
    """Main migration runner"""
    if len(sys.argv) < 2:
        print("Usage: python run_migrations.py [upgrade|downgrade|current|history|status]")
        sys.exit(1)
    
    command_type = sys.argv[1].lower()
    
    if command_type == "status":
        success = check_migration_status()
    else:
        success = run_migrations(command_type)
    
    if success:
        print(f"\nSUCCESS: Migration command '{command_type}' completed successfully")
    else:
        print(f"\nERROR: Migration command '{command_type}' failed")
        sys.exit(1)

if __name__ == "__main__":
    main()