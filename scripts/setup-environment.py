#!/usr/bin/env python3
"""
Python-based environment configuration management
Cross-platform alternative to shell scripts
"""

import os
import sys
import argparse
from pathlib import Path

def create_config_dir():
    """Create config directory if it doesn't exist"""
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    return config_dir

def generate_config(environment: str) -> Path:
    """Generate environment-specific configuration"""
    config_dir = create_config_dir()
    config_file = config_dir / f"{environment}.env"
    
    print(f"[CONFIG] Generating config for {environment} environment...")
    
    configs = {
        "development": """# Development Environment Configuration
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./data.db
JWT_SECRET_KEY=dev-secret-key-change-in-production
SENTRY_DSN=
POSTHOG_API_KEY=
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=false
LOG_LEVEL=DEBUG
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket
""",
        "staging": """# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=${STAGING_DATABASE_URL}
JWT_SECRET_KEY=${STAGING_JWT_SECRET_KEY}
SENTRY_DSN=${STAGING_SENTRY_DSN}
POSTHOG_API_KEY=${STAGING_POSTHOG_API_KEY}
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=true
LOG_LEVEL=INFO
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket
""",
        "production": """# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=${PRODUCTION_DATABASE_URL}
JWT_SECRET_KEY=${PRODUCTION_JWT_SECRET_KEY}
SENTRY_DSN=${PRODUCTION_SENTRY_DSN}
POSTHOG_API_KEY=${PRODUCTION_POSTHOG_API_KEY}
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=true
LOG_LEVEL=WARNING
BHIV_STORAGE_BACKEND=local
BHIV_BUCKET_PATH=bucket
# Security settings
SECURE_COOKIES=true
HTTPS_ONLY=true
HSTS_MAX_AGE=31536000
"""
    }
    
    if environment not in configs:
        print(f"[ERROR] Unknown environment: {environment}")
        sys.exit(1)
    
    config_file.write_text(configs[environment])
    print(f"[OK] Config generated: {config_file}")
    return config_file

def validate_config(environment: str) -> bool:
    """Validate configuration file"""
    config_dir = Path("config")
    config_file = config_dir / f"{environment}.env"
    
    print(f"[VALIDATE] Validating configuration for {environment}...")
    
    if not config_file.exists():
        print(f"[ERROR] Configuration file not found: {config_file}")
        return False
    
    content = config_file.read_text()
    required_vars = ["ENVIRONMENT", "DATABASE_URL", "JWT_SECRET_KEY"]
    
    if environment == "production":
        required_vars.extend(["SENTRY_DSN", "POSTHOG_API_KEY"])
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[ERROR] Missing required variables: {missing_vars}")
        return False
    
    print("[OK] Configuration validation passed")
    return True

def apply_config(environment: str) -> bool:
    """Apply configuration to .env file"""
    config_dir = Path("config")
    config_file = config_dir / f"{environment}.env"
    
    if not config_file.exists():
        print(f"[ERROR] Configuration file not found: {config_file}")
        return False
    
    print(f"[APPLY] Applying configuration from {config_file}")
    
    # Copy config to .env
    env_file = Path(".env")
    env_file.write_text(config_file.read_text())
    
    print("[OK] Configuration applied")
    return True

def main():
    parser = argparse.ArgumentParser(description="Environment configuration management")
    parser.add_argument("environment", choices=["development", "staging", "production"],
                       help="Target environment")
    parser.add_argument("action", choices=["generate", "apply", "validate"], 
                       default="generate", nargs="?",
                       help="Action to perform")
    
    args = parser.parse_args()
    
    print(f"[SETUP] Setting up configuration for environment: {args.environment}")
    
    if args.action == "generate":
        generate_config(args.environment)
        validate_config(args.environment)
    elif args.action == "apply":
        if not apply_config(args.environment):
            sys.exit(1)
    elif args.action == "validate":
        if not validate_config(args.environment):
            sys.exit(1)

if __name__ == "__main__":
    main()