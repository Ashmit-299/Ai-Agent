#!/bin/bash
# Environment-specific configuration management

set -e

ENVIRONMENT=${1:-development}
CONFIG_DIR="config"

echo "🔧 Setting up configuration for environment: $ENVIRONMENT"

# Create config directory if it doesn't exist
mkdir -p $CONFIG_DIR

# Function to generate environment-specific config
generate_config() {
    local env=$1
    local config_file="$CONFIG_DIR/$env.env"
    
    echo "📝 Generating config for $env environment..."
    
    case $env in
        "development")
            cat > $config_file << EOF
# Development Environment Configuration
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite:///./data.db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=dev-secret-key-change-in-production
SENTRY_DSN=
POSTHOG_API_KEY=
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=false
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
EOF
            ;;
        "staging")
            cat > $config_file << EOF
# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=false
DATABASE_URL=\${STAGING_DATABASE_URL}
REDIS_URL=\${STAGING_REDIS_URL}
JWT_SECRET_KEY=\${STAGING_JWT_SECRET_KEY}
SENTRY_DSN=\${STAGING_SENTRY_DSN}
POSTHOG_API_KEY=\${STAGING_POSTHOG_API_KEY}
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=true
LOG_LEVEL=INFO
CORS_ORIGINS=["https://staging.yourapp.com"]
EOF
            ;;
        "production")
            cat > $config_file << EOF
# Production Environment Configuration
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=\${PRODUCTION_DATABASE_URL}
REDIS_URL=\${PRODUCTION_REDIS_URL}
JWT_SECRET_KEY=\${PRODUCTION_JWT_SECRET_KEY}
SENTRY_DSN=\${PRODUCTION_SENTRY_DSN}
POSTHOG_API_KEY=\${PRODUCTION_POSTHOG_API_KEY}
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_USER_ANALYTICS=true
LOG_LEVEL=WARNING
CORS_ORIGINS=["https://yourapp.com"]
# Security settings
SECURE_COOKIES=true
HTTPS_ONLY=true
HSTS_MAX_AGE=31536000
EOF
            ;;
        *)
            echo "❌ Unknown environment: $env"
            exit 1
            ;;
    esac
    
    echo "✅ Config generated: $config_file"
}

# Function to validate configuration
validate_config() {
    local env=$1
    local config_file="$CONFIG_DIR/$env.env"
    
    echo "🔍 Validating configuration for $env..."
    
    # Check required variables
    required_vars=("ENVIRONMENT" "DATABASE_URL" "JWT_SECRET_KEY")
    
    if [ "$env" = "production" ]; then
        required_vars+=("SENTRY_DSN" "POSTHOG_API_KEY")
    fi
    
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" $config_file; then
            echo "❌ Missing required variable: $var"
            exit 1
        fi
    done
    
    echo "✅ Configuration validation passed"
}

# Function to apply configuration
apply_config() {
    local env=$1
    local config_file="$CONFIG_DIR/$env.env"
    
    if [ -f $config_file ]; then
        echo "📋 Applying configuration from $config_file"
        
        # Create .env file for the environment
        cp $config_file .env
        
        echo "✅ Configuration applied"
    else
        echo "❌ Configuration file not found: $config_file"
        exit 1
    fi
}

# Main execution
case "${2:-generate}" in
    "generate")
        generate_config $ENVIRONMENT
        validate_config $ENVIRONMENT
        ;;
    "apply")
        apply_config $ENVIRONMENT
        ;;
    "validate")
        validate_config $ENVIRONMENT
        ;;
    *)
        echo "Usage: $0 <environment> <action>"
        echo "Environments: development, staging, production"
        echo "Actions: generate, apply, validate"
        exit 1
        ;;
esac