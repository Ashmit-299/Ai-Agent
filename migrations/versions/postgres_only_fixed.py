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
    # First, modify user table to add user_id column
    op.add_column('user', sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('user', sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.alter_column('user', 'username', existing_type=sa.VARCHAR(), nullable=False)
    op.drop_index('ix_user_sub', table_name='user')
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_unique_constraint('uq_user_user_id', 'user', ['user_id'])
    
    # Create content table after user table is ready
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
    
    # Modify feedback table
    op.add_column('feedback', sa.Column('event_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    op.add_column('feedback', sa.Column('watch_time_ms', sa.Integer(), nullable=False))
    op.add_column('feedback', sa.Column('reward', sa.Float(), nullable=False))
    op.add_column('feedback', sa.Column('timestamp', sa.Float(), nullable=False))
    op.alter_column('feedback', 'user_id', existing_type=sa.INTEGER(), type_=sqlmodel.sql.sqltypes.AutoString(), nullable=False)
    op.drop_index('ix_feedback_content_id', table_name='feedback')
    op.drop_constraint('feedback_user_id_fkey', 'feedback', type_='foreignkey')
    op.create_foreign_key(None, 'feedback', 'user', ['user_id'], ['user_id'])
    op.create_foreign_key(None, 'feedback', 'content', ['content_id'], ['content_id'])
    op.drop_column('feedback', 'created_at')
    
    # Clean up old tables
    op.drop_index('ix_videometadata_content_id', table_name='videometadata')
    op.drop_table('videometadata')
    op.drop_index('ix_script_content_id', table_name='script')
    op.drop_table('script')
    
    # Clean up old user columns
    op.drop_column('user', 'sub')
    op.drop_column('user', 'id')


def downgrade() -> None:
    """Downgrade schema."""
    # This is a one-way migration for PostgreSQL enforcement
    pass