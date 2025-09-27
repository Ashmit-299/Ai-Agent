"""add missing tables and relationships

Revision ID: 004
Revises: 003
Create Date: 2025-01-20 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Create script table
    try:
        op.create_table('script',
            sa.Column('script_id', sa.String(), nullable=False),
            sa.Column('content_id', sa.String(), nullable=True),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('script_content', sa.Text(), nullable=False),
            sa.Column('script_type', sa.String(), nullable=True, default='text'),
            sa.Column('file_path', sa.String(), nullable=True),
            sa.Column('created_at', sa.Float(), nullable=False),
            sa.Column('used_for_generation', sa.Boolean(), nullable=True, default=False),
            sa.PrimaryKeyConstraint('script_id'),
            sa.ForeignKeyConstraint(['content_id'], ['content.content_id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE')
        )
        op.create_index('ix_script_user_id', 'script', ['user_id'])
        op.create_index('ix_script_content_id', 'script', ['content_id'])
    except Exception as e:
        print(f"Script table creation failed (may already exist): {e}")
    
    # Create videos table (separate from content for video-specific metadata)
    try:
        op.create_table('videos',
            sa.Column('video_id', sa.String(), nullable=False),
            sa.Column('content_id', sa.String(), nullable=False),
            sa.Column('script_id', sa.String(), nullable=True),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('file_path', sa.String(), nullable=False),
            sa.Column('thumbnail_path', sa.String(), nullable=True),
            sa.Column('duration_seconds', sa.Float(), nullable=True),
            sa.Column('resolution', sa.String(), nullable=True),
            sa.Column('frame_rate', sa.Float(), nullable=True),
            sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
            sa.Column('generation_method', sa.String(), nullable=True),
            sa.Column('processing_status', sa.String(), nullable=True, default='completed'),
            sa.Column('created_at', sa.Float(), nullable=False),
            sa.Column('updated_at', sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint('video_id'),
            sa.ForeignKeyConstraint(['content_id'], ['content.content_id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['script_id'], ['script.script_id'], ondelete='SET NULL')
        )
        op.create_index('ix_videos_content_id', 'videos', ['content_id'])
        op.create_index('ix_videos_script_id', 'videos', ['script_id'])
    except Exception as e:
        print(f"Videos table creation failed (may already exist): {e}")
    
    # Add foreign key constraints to existing tables
    try:
        # Add foreign keys to content table
        op.create_foreign_key('fk_content_uploader', 'content', 'user', ['uploader_id'], ['user_id'], ondelete='SET NULL')
    except Exception as e:
        print(f"Content foreign key creation failed (may already exist): {e}")
    
    try:
        # Add foreign keys to feedback table
        op.create_foreign_key('fk_feedback_content', 'feedback', 'content', ['content_id'], ['content_id'], ondelete='CASCADE')
        op.create_foreign_key('fk_feedback_user', 'feedback', 'user', ['user_id'], ['user_id'], ondelete='CASCADE')
    except Exception as e:
        print(f"Feedback foreign keys creation failed (may already exist): {e}")
    
    try:
        # Add foreign keys to analytics table
        op.create_foreign_key('fk_analytics_user', 'analytics', 'user', ['user_id'], ['user_id'], ondelete='SET NULL')
        op.create_foreign_key('fk_analytics_content', 'analytics', 'content', ['content_id'], ['content_id'], ondelete='SET NULL')
    except Exception as e:
        print(f"Analytics foreign keys creation failed (may already exist): {e}")
    
    try:
        # Add foreign keys to system_logs table
        op.create_foreign_key('fk_systemlogs_user', 'system_logs', 'user', ['user_id'], ['user_id'], ondelete='SET NULL')
    except Exception as e:
        print(f"System logs foreign key creation failed (may already exist): {e}")
    
    try:
        # Add foreign keys to invitations table
        op.create_foreign_key('fk_invitations_inviter', 'invitations', 'user', ['inviter_id'], ['user_id'], ondelete='CASCADE')
    except Exception as e:
        print(f"Invitations foreign key creation failed (may already exist): {e}")
    
    # Add indexes for better performance
    try:
        op.create_index('ix_content_uploader_id', 'content', ['uploader_id'])
        op.create_index('ix_content_uploaded_at', 'content', ['uploaded_at'])
        op.create_index('ix_feedback_content_id', 'feedback', ['content_id'])
        op.create_index('ix_feedback_user_id', 'feedback', ['user_id'])
        op.create_index('ix_feedback_timestamp', 'feedback', ['timestamp'])
        op.create_index('ix_analytics_event_type', 'analytics', ['event_type'])
        op.create_index('ix_analytics_timestamp', 'analytics', ['timestamp'])
        op.create_index('ix_systemlogs_level', 'system_logs', ['level'])
        op.create_index('ix_systemlogs_timestamp', 'system_logs', ['timestamp'])
    except Exception as e:
        print(f"Index creation failed (may already exist): {e}")

def downgrade():
    try:
        # Drop foreign key constraints
        op.drop_constraint('fk_invitations_inviter', 'invitations', type_='foreignkey')
        op.drop_constraint('fk_systemlogs_user', 'system_logs', type_='foreignkey')
        op.drop_constraint('fk_analytics_content', 'analytics', type_='foreignkey')
        op.drop_constraint('fk_analytics_user', 'analytics', type_='foreignkey')
        op.drop_constraint('fk_feedback_user', 'feedback', type_='foreignkey')
        op.drop_constraint('fk_feedback_content', 'feedback', type_='foreignkey')
        op.drop_constraint('fk_content_uploader', 'content', type_='foreignkey')
        
        # Drop indexes
        op.drop_index('ix_systemlogs_timestamp', 'system_logs')
        op.drop_index('ix_systemlogs_level', 'system_logs')
        op.drop_index('ix_analytics_timestamp', 'analytics')
        op.drop_index('ix_analytics_event_type', 'analytics')
        op.drop_index('ix_feedback_timestamp', 'feedback')
        op.drop_index('ix_feedback_user_id', 'feedback')
        op.drop_index('ix_feedback_content_id', 'feedback')
        op.drop_index('ix_content_uploaded_at', 'content')
        op.drop_index('ix_content_uploader_id', 'content')
        
        # Drop new tables
        op.drop_index('ix_videos_script_id', 'videos')
        op.drop_index('ix_videos_content_id', 'videos')
        op.drop_table('videos')
        
        op.drop_index('ix_script_content_id', 'script')
        op.drop_index('ix_script_user_id', 'script')
        op.drop_table('script')
    except Exception as e:
        print(f"Downgrade failed: {e}")