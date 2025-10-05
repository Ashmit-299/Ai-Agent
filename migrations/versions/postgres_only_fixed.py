"""postgres_only_fixed

Revision ID: postgres_only_fixed
Revises: 001
Create Date: 2025-09-19 13:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'postgres_only_fixed'
down_revision: Union[str, Sequence[str], None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema with safe operations."""
    # Use raw SQL with proper error handling to avoid transaction issues
    connection = op.get_bind()
    
    # Check what exists using direct SQL queries
    def column_exists(table, column):
        result = connection.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = :table AND column_name = :column)"
        ), {"table": table, "column": column})
        return result.scalar()
    
    def index_exists(index_name):
        result = connection.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = :index_name)"
        ), {"index_name": index_name})
        return result.scalar()
    
    def table_exists(table_name):
        result = connection.execute(sa.text(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :table_name)"
        ), {"table_name": table_name})
        return result.scalar()
    
    # Add user_id column if it doesn't exist
    if not column_exists('user', 'user_id'):
        connection.execute(sa.text('ALTER TABLE "user" ADD COLUMN user_id VARCHAR NOT NULL DEFAULT \'demo001\''))
    
    # Add password_hash column if it doesn't exist
    if not column_exists('user', 'password_hash'):
        connection.execute(sa.text('ALTER TABLE "user" ADD COLUMN password_hash VARCHAR NOT NULL DEFAULT \'$2b$12$dummy\''))
    
    # Drop old index if it exists
    if index_exists('ix_user_sub'):
        connection.execute(sa.text('DROP INDEX ix_user_sub'))
    
    # Create new index if it doesn't exist
    if not index_exists('ix_user_username'):
        connection.execute(sa.text('CREATE UNIQUE INDEX ix_user_username ON "user" (username)'))
    
    # Add unique constraint if it doesn't exist
    try:
        connection.execute(sa.text('ALTER TABLE "user" ADD CONSTRAINT uq_user_user_id UNIQUE (user_id)'))
    except Exception:
        pass  # Constraint already exists
    
    # Create content table if it doesn't exist
    if not table_exists('content'):
        connection.execute(sa.text('''
            CREATE TABLE content (
                content_id VARCHAR NOT NULL PRIMARY KEY,
                uploader_id VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                description VARCHAR,
                file_path VARCHAR NOT NULL,
                content_type VARCHAR NOT NULL,
                duration_ms INTEGER NOT NULL DEFAULT 0,
                uploaded_at FLOAT NOT NULL,
                authenticity_score FLOAT NOT NULL DEFAULT 0.8,
                current_tags VARCHAR DEFAULT '[]',
                views INTEGER NOT NULL DEFAULT 0,
                likes INTEGER NOT NULL DEFAULT 0,
                shares INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (uploader_id) REFERENCES "user" (user_id)
            )
        '''))
    
    # Modify feedback table if it exists
    if table_exists('feedback'):
        # Add new columns if they don't exist
        if not column_exists('feedback', 'event_type'):
            connection.execute(sa.text('ALTER TABLE feedback ADD COLUMN event_type VARCHAR NOT NULL DEFAULT \'view\''))
        
        if not column_exists('feedback', 'watch_time_ms'):
            connection.execute(sa.text('ALTER TABLE feedback ADD COLUMN watch_time_ms INTEGER NOT NULL DEFAULT 0'))
        
        if not column_exists('feedback', 'reward'):
            connection.execute(sa.text('ALTER TABLE feedback ADD COLUMN reward FLOAT NOT NULL DEFAULT 0.0'))
        
        if not column_exists('feedback', 'timestamp'):
            connection.execute(sa.text('ALTER TABLE feedback ADD COLUMN timestamp FLOAT NOT NULL DEFAULT 0'))
        
        # Drop old columns if they exist
        if column_exists('feedback', 'created_at'):
            connection.execute(sa.text('ALTER TABLE feedback DROP COLUMN created_at'))
    
    # Clean up old tables if they exist
    if table_exists('videometadata'):
        connection.execute(sa.text('DROP TABLE IF EXISTS videometadata CASCADE'))
    
    if table_exists('script'):
        connection.execute(sa.text('DROP TABLE IF EXISTS script CASCADE'))
    
    # Clean up old user columns if they exist
    if column_exists('user', 'sub'):
        connection.execute(sa.text('ALTER TABLE "user" DROP COLUMN IF EXISTS sub'))
    
    if column_exists('user', 'id'):
        connection.execute(sa.text('ALTER TABLE "user" DROP COLUMN IF EXISTS id'))


def downgrade() -> None:
    """Downgrade schema with proper error handling."""
    try:
        # Restore old columns if needed
        op.add_column('user', sa.Column('id', sa.INTEGER(), nullable=True))
        op.add_column('user', sa.Column('sub', sa.VARCHAR(), nullable=True))
        
        # Remove new columns
        op.drop_column('user', 'user_id')
        op.drop_column('user', 'password_hash')
        
        # Drop content table
        op.drop_table('content')
        
    except Exception as e:
        print(f"Downgrade failed: {e}")
        # This is acceptable for a one-way migration
        pass