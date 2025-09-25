#!/usr/bin/env python3
"""
Production-ready migration runner with error handling and rollback support
"""
import os
import sys
import logging
from pathlib import Path
from alembic.config import Config
from alembic import command
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MigrationManager:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data.db")
        self.alembic_cfg = Config("alembic.ini")
        self.alembic_cfg.set_main_option("sqlalchemy.url", self.database_url)
        
    def check_database_connection(self):
        """Test database connectivity before running migrations"""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                # Test basic query
                if self.database_url.startswith("postgresql"):
                    conn.execute(text("SELECT 1"))
                else:
                    conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def get_current_revision(self):
        """Get current database revision"""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                return current_rev
        except Exception as e:
            logger.warning(f"Could not get current revision: {e}")
            return None
    
    def get_available_revisions(self):
        """Get list of available migration revisions"""
        try:
            script = ScriptDirectory.from_config(self.alembic_cfg)
            revisions = list(script.walk_revisions())
            return [rev.revision for rev in revisions]
        except Exception as e:
            logger.error(f"Failed to get available revisions: {e}")
            return []
    
    def create_tables_if_not_exist(self):
        """Create tables using SQLModel if no migrations exist"""
        try:
            from ..core.database import engine
            SQLModel.metadata.create_all(engine)
            logger.info("✅ Created tables using SQLModel")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def run_migrations(self, target_revision="head"):
        """Run database migrations with error handling"""
        logger.info("🚀 Starting database migration process...")
        
        # Check database connection
        if not self.check_database_connection():
            return False
        
        try:
            # Get current state
            current_rev = self.get_current_revision()
            available_revs = self.get_available_revisions()
            
            logger.info(f"Current revision: {current_rev or 'None'}")
            logger.info(f"Available revisions: {len(available_revs)}")
            
            # If no current revision and no alembic_version table, create tables first
            if current_rev is None and not self._alembic_version_table_exists():
                logger.info("No migration history found. Creating initial tables...")
                
                # Try to stamp with base revision first
                if available_revs:
                    command.stamp(self.alembic_cfg, "base")
                    logger.info("✅ Stamped database with base revision")
            
            # Run migrations
            logger.info(f"Upgrading to {target_revision}...")
            command.upgrade(self.alembic_cfg, target_revision)
            
            # Verify final state
            final_rev = self.get_current_revision()
            logger.info(f"✅ Migration completed successfully. Final revision: {final_rev}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            logger.error("Consider manual rollback if needed")
            return False
    
    def _alembic_version_table_exists(self):
        """Check if alembic_version table exists"""
        try:
            engine = create_engine(self.database_url)
            with engine.connect() as conn:
                if self.database_url.startswith("postgresql"):
                    result = conn.execute(text("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'alembic_version'
                        );
                    """))
                else:
                    result = conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='alembic_version';
                    """))
                return bool(result.fetchone())
        except Exception:
            return False
    
    def rollback_to_revision(self, target_revision):
        """Rollback to specific revision"""
        logger.info(f"🔄 Rolling back to revision: {target_revision}")
        try:
            command.downgrade(self.alembic_cfg, target_revision)
            logger.info("✅ Rollback completed successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def create_migration(self, message):
        """Create new migration file"""
        logger.info(f"📝 Creating new migration: {message}")
        try:
            command.revision(self.alembic_cfg, message=message, autogenerate=True)
            logger.info("✅ Migration file created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create migration: {e}")
            return False

def main():
    """Main migration runner"""
    manager = MigrationManager()
    
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "upgrade":
            target = sys.argv[2] if len(sys.argv) > 2 else "head"
            success = manager.run_migrations(target)
        elif action == "rollback":
            if len(sys.argv) < 3:
                logger.error("Please specify target revision for rollback")
                sys.exit(1)
            target = sys.argv[2]
            success = manager.rollback_to_revision(target)
        elif action == "create":
            if len(sys.argv) < 3:
                logger.error("Please specify migration message")
                sys.exit(1)
            message = " ".join(sys.argv[2:])
            success = manager.create_migration(message)
        else:
            logger.error(f"Unknown action: {action}")
            logger.info("Available actions: upgrade, rollback, create")
            sys.exit(1)
    else:
        # Default: run migrations
        success = manager.run_migrations()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()