"""Database configuration with IPv4 Supabase connection"""

import os
from .config import DATABASE_URL

def get_database_url():
    """Get Supabase database URL with IPv4 transaction pooler"""
    # Use IPv4 transaction pooler for compatibility
    return os.getenv("DATABASE_URL", "postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")

def get_engine_args():
    """Get SQLAlchemy engine arguments for Supabase"""
    return {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 5,
        "max_overflow": 10,
        "connect_args": {
            "connect_timeout": 10,
            "sslmode": "require"
        }
    }