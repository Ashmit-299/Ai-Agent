"""add advanced features

Revision ID: 003
Revises: 001
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Add missing columns to user table
    try:
        op.add_column('user', sa.Column('email_verified', sa.Boolean(), default=False))
        op.add_column('user', sa.Column('verification_token', sa.String(), nullable=True))
        op.add_column('user', sa.Column('role', sa.String(), default='user'))
        op.add_column('user', sa.Column('last_login', sa.Float(), nullable=True))
    except Exception:
        pass  # Columns may already exist
    
    # Add missing columns to content table
    try:
        op.add_column('content', sa.Column('duration_ms', sa.Integer(), nullable=True))
        op.add_column('content', sa.Column('views', sa.Integer(), default=0))
        op.add_column('content', sa.Column('likes', sa.Integer(), default=0))
        op.add_column('content', sa.Column('shares', sa.Integer(), default=0))
        op.add_column('content', sa.Column('status', sa.String(), default='active'))
    except Exception:
        pass  # Columns may already exist
    
    # Add missing columns to feedback table
    try:
        op.add_column('feedback', sa.Column('watch_time_ms', sa.Integer(), nullable=True))
        op.add_column('feedback', sa.Column('reward', sa.Float(), nullable=True))
        op.add_column('feedback', sa.Column('ip_address', sa.String(), nullable=True))
    except Exception:
        pass  # Columns may already exist
    
    # Create invitations table
    try:
        op.create_table('invitations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(), nullable=False),
            sa.Column('inviter_id', sa.String(), nullable=False),
            sa.Column('invitation_token', sa.String(), nullable=False),
            sa.Column('created_at', sa.Float(), nullable=False),
            sa.Column('expires_at', sa.Float(), nullable=False),
            sa.Column('used', sa.Boolean(), default=False),
            sa.Column('used_at', sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('invitation_token')
        )
    except Exception:
        pass  # Table may already exist
    
    # Create analytics table
    try:
        op.create_table('analytics',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('event_type', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=True),
            sa.Column('content_id', sa.String(), nullable=True),
            sa.Column('metadata', sa.Text(), nullable=True),
            sa.Column('timestamp', sa.Float(), nullable=False),
            sa.Column('ip_address', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    except Exception:
        pass  # Table may already exist
    
    # Create system_logs table
    try:
        op.create_table('system_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('level', sa.String(), nullable=False),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('module', sa.String(), nullable=True),
            sa.Column('timestamp', sa.Float(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    except Exception:
        pass  # Table may already exist

def downgrade():
    try:
        op.drop_table('system_logs')
        op.drop_table('analytics')
        op.drop_table('invitations')
        
        # Remove added columns (optional - may cause data loss)
        op.drop_column('feedback', 'ip_address')
        op.drop_column('feedback', 'reward')
        op.drop_column('feedback', 'watch_time_ms')
        
        op.drop_column('content', 'status')
        op.drop_column('content', 'shares')
        op.drop_column('content', 'likes')
        op.drop_column('content', 'views')
        op.drop_column('content', 'duration_ms')
        
        op.drop_column('user', 'last_login')
        op.drop_column('user', 'role')
        op.drop_column('user', 'verification_token')
        op.drop_column('user', 'email_verified')
    except Exception:
        pass  # Ignore errors during downgrade