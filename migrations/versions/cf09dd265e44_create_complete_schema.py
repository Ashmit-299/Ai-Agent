"""create complete schema

Revision ID: cf09dd265e44
Revises: 
Create Date: 2025-01-02 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cf09dd265e44'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Create complete schema safely."""
    connection = op.get_bind()
    
    # Create all tables with proper error handling
    connection.execute(sa.text("""
        -- Create user table
        CREATE TABLE IF NOT EXISTS "user" (
            user_id VARCHAR PRIMARY KEY,
            username VARCHAR UNIQUE NOT NULL,
            password_hash VARCHAR NOT NULL,
            email VARCHAR,
            created_at FLOAT NOT NULL DEFAULT EXTRACT(EPOCH FROM NOW()),
            is_active BOOLEAN DEFAULT TRUE
        );
        
        -- Create content table
        CREATE TABLE IF NOT EXISTS content (
            content_id VARCHAR PRIMARY KEY,
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
        );
        
        -- Create feedback table
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id SERIAL PRIMARY KEY,
            user_id VARCHAR NOT NULL,
            content_id VARCHAR NOT NULL,
            event_type VARCHAR NOT NULL DEFAULT 'view',
            watch_time_ms INTEGER NOT NULL DEFAULT 0,
            reward FLOAT NOT NULL DEFAULT 0.0,
            timestamp FLOAT NOT NULL,
            rating INTEGER,
            comment TEXT,
            FOREIGN KEY (user_id) REFERENCES "user" (user_id),
            FOREIGN KEY (content_id) REFERENCES content (content_id)
        );
        
        -- Create script table
        CREATE TABLE IF NOT EXISTS script (
            script_id VARCHAR PRIMARY KEY,
            content_id VARCHAR,
            user_id VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            script_content TEXT NOT NULL,
            script_type VARCHAR,
            file_path VARCHAR,
            created_at FLOAT NOT NULL,
            used_for_generation BOOLEAN DEFAULT FALSE,
            version VARCHAR,
            script_metadata TEXT,
            FOREIGN KEY (content_id) REFERENCES content (content_id),
            FOREIGN KEY (user_id) REFERENCES "user" (user_id)
        );
        
        -- Create audit_logs table
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR,
            action VARCHAR NOT NULL,
            resource_type VARCHAR NOT NULL,
            resource_id VARCHAR NOT NULL,
            timestamp FLOAT NOT NULL,
            ip_address VARCHAR,
            user_agent VARCHAR,
            request_id VARCHAR,
            details TEXT,
            status VARCHAR
        );
        
        -- Create analytics table
        CREATE TABLE IF NOT EXISTS analytics (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR,
            event_type VARCHAR NOT NULL,
            event_data TEXT,
            timestamp FLOAT NOT NULL,
            session_id VARCHAR,
            FOREIGN KEY (user_id) REFERENCES "user" (user_id)
        );
        
        -- Create system_logs table
        CREATE TABLE IF NOT EXISTS system_logs (
            id SERIAL PRIMARY KEY,
            level VARCHAR NOT NULL,
            message TEXT NOT NULL,
            timestamp FLOAT NOT NULL,
            module VARCHAR,
            function VARCHAR,
            line_number INTEGER,
            extra_data TEXT
        );
    """))
    
    # Create indexes safely
    connection.execute(sa.text("""
        -- User indexes
        CREATE INDEX IF NOT EXISTS ix_user_username ON "user" (username);
        CREATE INDEX IF NOT EXISTS ix_user_created_at ON "user" (created_at);
        
        -- Content indexes
        CREATE INDEX IF NOT EXISTS ix_content_uploader_id ON content (uploader_id);
        CREATE INDEX IF NOT EXISTS ix_content_uploaded_at ON content (uploaded_at);
        CREATE INDEX IF NOT EXISTS ix_content_content_type ON content (content_type);
        
        -- Feedback indexes
        CREATE INDEX IF NOT EXISTS ix_feedback_user_id ON feedback (user_id);
        CREATE INDEX IF NOT EXISTS ix_feedback_content_id ON feedback (content_id);
        CREATE INDEX IF NOT EXISTS ix_feedback_timestamp ON feedback (timestamp);
        
        -- Script indexes
        CREATE INDEX IF NOT EXISTS ix_script_user_id ON script (user_id);
        CREATE INDEX IF NOT EXISTS ix_script_content_id ON script (content_id);
        CREATE INDEX IF NOT EXISTS ix_script_created_at ON script (created_at);
        
        -- Audit logs indexes
        CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs (user_id);
        CREATE INDEX IF NOT EXISTS ix_audit_logs_action ON audit_logs (action);
        CREATE INDEX IF NOT EXISTS ix_audit_logs_resource_type ON audit_logs (resource_type);
        CREATE INDEX IF NOT EXISTS ix_audit_logs_timestamp ON audit_logs (timestamp);
        CREATE INDEX IF NOT EXISTS ix_audit_logs_request_id ON audit_logs (request_id);
        
        -- Analytics indexes
        CREATE INDEX IF NOT EXISTS ix_analytics_user_id ON analytics (user_id);
        CREATE INDEX IF NOT EXISTS ix_analytics_event_type ON analytics (event_type);
        CREATE INDEX IF NOT EXISTS ix_analytics_timestamp ON analytics (timestamp);
        
        -- System logs indexes
        CREATE INDEX IF NOT EXISTS ix_system_logs_level ON system_logs (level);
        CREATE INDEX IF NOT EXISTS ix_system_logs_timestamp ON system_logs (timestamp);
        CREATE INDEX IF NOT EXISTS ix_system_logs_module ON system_logs (module);
    """))

def downgrade() -> None:
    """Drop all tables."""
    connection = op.get_bind()
    connection.execute(sa.text("""
        DROP TABLE IF EXISTS system_logs CASCADE;
        DROP TABLE IF EXISTS analytics CASCADE;
        DROP TABLE IF EXISTS audit_logs CASCADE;
        DROP TABLE IF EXISTS script CASCADE;
        DROP TABLE IF EXISTS feedback CASCADE;
        DROP TABLE IF EXISTS content CASCADE;
        DROP TABLE IF EXISTS "user" CASCADE;
    """))