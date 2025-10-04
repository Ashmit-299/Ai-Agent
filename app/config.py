"""Configuration loader for Task 6 credentials and environment variables"""

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Production Credentials
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWS_SECRET = JWT_SECRET_KEY  # Backwards compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres.dusqpdhojbgfxwflukhc:Moto%40Roxy123@aws-1-ap-south-1.pooler.supabase.com:6543/postgres")
POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")
SENTRY_DSN = os.getenv("SENTRY_DSN")

# Storage configuration
BHIV_STORAGE_BACKEND = os.getenv("BHIV_STORAGE_BACKEND", "local")
BHIV_BUCKET_PATH = os.getenv("BHIV_BUCKET_PATH", "bucket")

def validate_config():
    """Validate that required configuration is present"""
    required_vars = {
        "JWT_SECRET_KEY": JWT_SECRET_KEY,
        "DATABASE_URL": DATABASE_URL,
        "POSTHOG_API_KEY": POSTHOG_API_KEY,
        "SENTRY_DSN": SENTRY_DSN
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        print(f"Warning: Missing required environment variables: {', '.join(missing)}")
        return False
    
    return True

def get_config():
    """Get configuration dictionary"""
    return {
        "jws_secret": JWS_SECRET,
        "database_url": DATABASE_URL,
        "posthog_api_key": POSTHOG_API_KEY,
        "sentry_dsn": SENTRY_DSN,
        "jwt_secret_key": JWT_SECRET_KEY,
        "storage_backend": BHIV_STORAGE_BACKEND,
        "bucket_path": BHIV_BUCKET_PATH
    }