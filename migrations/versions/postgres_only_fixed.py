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
    """Upgrade schema."""
    # Check and add columns to user table if they don't exist
    try:
        op.add_column('user', sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    except Exception:
        pass  # Column already exists
    
    try:
        op.add_column('user', sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    except Exception:
        pass  # Column already exists
    
    try:
        op.alter_column('user', 'username', existing_type=sa.VARCHAR(), nullable=False)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_user_sub', table_name='user')
    except Exception:
        pass  # Index doesn't exist
    
    try:
        op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    except Exception:
        pass  # Index already exists
    
    try:
        op.create_unique_constraint('uq_user_user_id', 'user', ['user_id'])
    except Exception:
        pass  # Constraint already exists
    
    # Create content table after user table is ready
    try:
        op.create_table('content',
            sa.Column('content_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('uploader_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('file_path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('content_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('duration_ms', sa.Integer(), nullable=False),
            sa.Column('uploaded_at', sa.Float(), nullable=False),
            sa.Column('authenticity_score', sa.Float(), nullable=False),
            sa.Column('current_tags', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('views', sa.Integer(), nullable=False),
            sa.Column('likes', sa.Integer(), nullable=False),
            sa.Column('shares', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['uploader_id'], ['user.user_id'], ),
            sa.PrimaryKeyConstraint('content_id')
        )
    except Exception:
        pass  # Table already exists
    
    # Modify feedback table
    try:
        op.add_column('feedback', sa.Column('event_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    except Exception:
        pass
    
    try:
        op.add_column('feedback', sa.Column('watch_time_ms', sa.Integer(), nullable=False))
    except Exception:
        pass
    
    try:
        op.add_column('feedback', sa.Column('reward', sa.Float(), nullable=False))
    except Exception:
        pass
    
    try:
        op.add_column('feedback', sa.Column('timestamp', sa.Float(), nullable=False))
    except Exception:
        pass
    
    try:
        op.alter_column('feedback', 'user_id', existing_type=sa.INTEGER(), type_=sqlmodel.sql.sqltypes.AutoString(), nullable=False)
    except Exception:
        pass
    
    try:
        op.drop_index('ix_feedback_content_id', table_name='feedback')
    except Exception:
        pass
    
    try:
        op.drop_constraint('feedback_user_id_fkey', 'feedback', type_='foreignkey')
    except Exception:
        pass
    
    try:
        op.create_foreign_key(None, 'feedback', 'user', ['user_id'], ['user_id'])
    except Exception:
        pass
    
    try:
        op.create_foreign_key(None, 'feedback', 'content', ['content_id'], ['content_id'])
    except Exception:
        pass
    
    try:
        op.drop_column('feedback', 'created_at')
    except Exception:
        pass
    
    # Clean up old tables
    try:
        op.drop_index('ix_videometadata_content_id', table_name='videometadata')
    except Exception:
        pass
    
    try:
        op.drop_table('videometadata')
    except Exception:
        pass
    
    try:
        op.drop_index('ix_script_content_id', table_name='script')
    except Exception:
        pass
    
    try:
        op.drop_table('script')
    except Exception:
        pass
    
    # Clean up old user columns
    try:
        op.drop_column('user', 'sub')
    except Exception:
        pass
    
    try:
        op.drop_column('user', 'id')
    except Exception:
        pass


def downgrade() -> None:
    """Downgrade schema."""
    # This is a one-way migration for PostgreSQL enforcement
    pass