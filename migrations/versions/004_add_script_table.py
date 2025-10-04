"""add script table

Revision ID: 004
Revises: 003
Create Date: 2025-10-03 10:41:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade():
    # Create script table with proper foreign key constraints
    try:
        op.create_table('script',
            sa.Column('script_id', sa.String(), nullable=False),
            sa.Column('content_id', sa.String(), nullable=True),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('title', sa.String(), nullable=False),
            sa.Column('script_content', sa.Text(), nullable=False),
            sa.Column('script_type', sa.String(), nullable=True),
            sa.Column('file_path', sa.String(), nullable=True),
            sa.Column('created_at', sa.Float(), nullable=False),
            sa.Column('used_for_generation', sa.Boolean(), default=False),
            sa.Column('version', sa.String(), nullable=True),
            sa.Column('script_metadata', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('script_id'),
            sa.ForeignKeyConstraint(['content_id'], ['content.content_id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
            sa.Index('ix_script_content_id', 'content_id'),
            sa.Index('ix_script_user_id', 'user_id'),
            sa.Index('ix_script_created_at', 'created_at')
        )
        print("Script table created successfully")
    except Exception as e:
        print(f"Script table creation failed (may already exist): {e}")
        pass

    # Add missing indexes for performance
    try:
        op.create_index('ix_content_uploader_id', 'content', ['uploader_id'])
        op.create_index('ix_content_uploaded_at', 'content', ['uploaded_at'])
        op.create_index('ix_feedback_content_id', 'feedback', ['content_id'])
        op.create_index('ix_feedback_user_id', 'feedback', ['user_id'])
        op.create_index('ix_feedback_timestamp', 'feedback', ['timestamp'])
    except Exception as e:
        print(f"Index creation failed (may already exist): {e}")
        pass

    # Create audit_logs table for comprehensive logging
    try:
        op.create_table('audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=True),
            sa.Column('action', sa.String(), nullable=False),
            sa.Column('resource_type', sa.String(), nullable=False),
            sa.Column('resource_id', sa.String(), nullable=False),
            sa.Column('timestamp', sa.Float(), nullable=False),
            sa.Column('ip_address', sa.String(), nullable=True),
            sa.Column('user_agent', sa.String(), nullable=True),
            sa.Column('request_id', sa.String(), nullable=True),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('status', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.Index('ix_audit_logs_user_id', 'user_id'),
            sa.Index('ix_audit_logs_action', 'action'),
            sa.Index('ix_audit_logs_resource_type', 'resource_type'),
            sa.Index('ix_audit_logs_timestamp', 'timestamp'),
            sa.Index('ix_audit_logs_request_id', 'request_id')
        )
        print("Audit logs table created successfully")
    except Exception as e:
        print(f"Audit logs table creation failed (may already exist): {e}")
        pass

def downgrade():
    try:
        op.drop_table('audit_logs')
        op.drop_table('script')
        # Remove indexes
        op.drop_index('ix_content_uploader_id', 'content')
        op.drop_index('ix_content_uploaded_at', 'content')
        op.drop_index('ix_feedback_content_id', 'feedback')
        op.drop_index('ix_feedback_user_id', 'feedback')
        op.drop_index('ix_feedback_timestamp', 'feedback')
    except Exception:
        pass