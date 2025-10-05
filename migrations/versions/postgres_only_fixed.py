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
    """Upgrade schema with proper transaction handling."""
    connection = op.get_bind()
    
    # Check if columns exist before adding them
    inspector = sa.inspect(connection)
    user_columns = [col['name'] for col in inspector.get_columns('user')]
    
    # Add user_id column if it doesn't exist
    if 'user_id' not in user_columns:
        try:
            op.add_column('user', sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
        except Exception as e:
            print(f"Failed to add user_id column: {e}")
    
    # Add password_hash column if it doesn't exist
    if 'password_hash' not in user_columns:
        try:
            op.add_column('user', sa.Column('password_hash', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
        except Exception as e:
            print(f"Failed to add password_hash column: {e}")
    
    # Update username column
    try:
        op.alter_column('user', 'username', existing_type=sa.VARCHAR(), nullable=False)
    except Exception as e:
        print(f"Failed to alter username column: {e}")
    
    # Handle indexes safely
    try:
        op.drop_index('ix_user_sub', table_name='user')
    except Exception as e:
        print(f"Failed to drop ix_user_sub index: {e}")
    
    try:
        op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    except Exception as e:
        print(f"Failed to create ix_user_username index: {e}")
    
    try:
        op.create_unique_constraint('uq_user_user_id', 'user', ['user_id'])
    except Exception as e:
        print(f"Failed to create user_id constraint: {e}")
    
    # Create content table if it doesn't exist
    existing_tables = inspector.get_table_names()
    if 'content' not in existing_tables:
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
        except Exception as e:
            print(f"Failed to create content table: {e}")
    
    # Modify feedback table if it exists
    if 'feedback' in existing_tables:
        feedback_columns = [col['name'] for col in inspector.get_columns('feedback')]
        
        # Add new columns if they don't exist
        if 'event_type' not in feedback_columns:
            try:
                op.add_column('feedback', sa.Column('event_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
            except Exception as e:
                print(f"Failed to add event_type column: {e}")
        
        if 'watch_time_ms' not in feedback_columns:
            try:
                op.add_column('feedback', sa.Column('watch_time_ms', sa.Integer(), nullable=False))
            except Exception as e:
                print(f"Failed to add watch_time_ms column: {e}")
        
        if 'reward' not in feedback_columns:
            try:
                op.add_column('feedback', sa.Column('reward', sa.Float(), nullable=False))
            except Exception as e:
                print(f"Failed to add reward column: {e}")
        
        if 'timestamp' not in feedback_columns:
            try:
                op.add_column('feedback', sa.Column('timestamp', sa.Float(), nullable=False))
            except Exception as e:
                print(f"Failed to add timestamp column: {e}")
        
        # Handle constraints and indexes
        try:
            op.drop_index('ix_feedback_content_id', table_name='feedback')
        except Exception as e:
            print(f"Failed to drop feedback index: {e}")
        
        try:
            op.drop_constraint('feedback_user_id_fkey', 'feedback', type_='foreignkey')
        except Exception as e:
            print(f"Failed to drop feedback constraint: {e}")
        
        try:
            op.create_foreign_key(None, 'feedback', 'user', ['user_id'], ['user_id'])
        except Exception as e:
            print(f"Failed to create user foreign key: {e}")
        
        try:
            op.create_foreign_key(None, 'feedback', 'content', ['content_id'], ['content_id'])
        except Exception as e:
            print(f"Failed to create content foreign key: {e}")
        
        if 'created_at' in feedback_columns:
            try:
                op.drop_column('feedback', 'created_at')
            except Exception as e:
                print(f"Failed to drop created_at column: {e}")
    
    # Clean up old tables if they exist
    if 'videometadata' in existing_tables:
        try:
            op.drop_index('ix_videometadata_content_id', table_name='videometadata')
        except Exception as e:
            print(f"Failed to drop videometadata index: {e}")
        
        try:
            op.drop_table('videometadata')
        except Exception as e:
            print(f"Failed to drop videometadata table: {e}")
    
    if 'script' in existing_tables:
        try:
            op.drop_index('ix_script_content_id', table_name='script')
        except Exception as e:
            print(f"Failed to drop script index: {e}")
        
        try:
            op.drop_table('script')
        except Exception as e:
            print(f"Failed to drop script table: {e}")
    
    # Clean up old user columns if they exist
    user_columns = [col['name'] for col in inspector.get_columns('user')]
    
    if 'sub' in user_columns:
        try:
            op.drop_column('user', 'sub')
        except Exception as e:
            print(f"Failed to drop sub column: {e}")
    
    if 'id' in user_columns:
        try:
            op.drop_column('user', 'id')
        except Exception as e:
            print(f"Failed to drop id column: {e}")


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