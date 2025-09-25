#!/bin/bash
# Automated rollback system for failed deployments

set -e

ENVIRONMENT=${1:-production}
ROLLBACK_TARGET=${2:-previous}

echo "🔄 Initiating rollback for $ENVIRONMENT environment"

# Function to get previous working version
get_previous_version() {
    if command -v git &> /dev/null; then
        PREVIOUS_VERSION=$(git describe --tags --abbrev=0 HEAD~1 2>/dev/null || echo "")
        if [ -z "$PREVIOUS_VERSION" ]; then
            PREVIOUS_VERSION=$(git rev-parse HEAD~1 | cut -c1-8)
        fi
    else
        PREVIOUS_VERSION="latest"
    fi
    
    echo $PREVIOUS_VERSION
}

# Function to backup current state
backup_current_state() {
    echo "💾 Creating backup of current state..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup database (if PostgreSQL)
    if [ -n "$DATABASE_URL" ] && [[ "$DATABASE_URL" == postgresql* ]]; then
        echo "📊 Backing up database..."
        pg_dump "$DATABASE_URL" > "$BACKUP_DIR/database_backup.sql" || {
            echo "⚠️ Database backup failed, continuing rollback..."
        }
    fi
    
    # Backup application logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/" || true
    fi
    
    # Store current version info
    echo "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')" > "$BACKUP_DIR/current_version.txt"
    
    echo "✅ Backup created in $BACKUP_DIR"
}

# Function to perform rollback
perform_rollback() {
    local target_version=$1
    
    echo "🔄 Rolling back to version: $target_version"
    
    # Rollback application deployment
    case $ENVIRONMENT in
        "production")
            rollback_production $target_version
            ;;
        "staging") 
            rollback_staging $target_version
            ;;
        *)
            echo "❌ Rollback not configured for environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
}

# Function to rollback production deployment
rollback_production() {
    local version=$1
    
    echo "🏭 Rolling back production deployment..."
    
    # For Render deployment
    if [ -n "$RENDER_API_KEY" ] && [ -n "$RENDER_PRODUCTION_SERVICE_ID" ]; then
        curl -X POST "https://api.render.com/v1/services/$RENDER_PRODUCTION_SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"imageUrl\": \"ashmitpandey299/ai-uploader-agent:$version\",
                \"clearCache\": \"clear\"
            }"
    fi
    
    # For Docker Compose deployment
    if [ -f "docker-compose.prod.yml" ]; then
        export IMAGE_TAG=$version
        docker-compose -f docker-compose.prod.yml up -d
    fi
}

# Function to rollback staging deployment  
rollback_staging() {
    local version=$1
    
    echo "🧪 Rolling back staging deployment..."
    
    if [ -n "$RENDER_API_KEY" ] && [ -n "$RENDER_STAGING_SERVICE_ID" ]; then
        curl -X POST "https://api.render.com/v1/services/$RENDER_STAGING_SERVICE_ID/deploys" \
            -H "Authorization: Bearer $RENDER_API_KEY" \
            -H "Content-Type: application/json" \
            -d "{
                \"imageUrl\": \"ashmitpandey299/ai-uploader-agent:$version\",
                \"clearCache\": \"clear\"
            }"
    fi
}

# Function to verify rollback
verify_rollback() {
    local api_url=$1
    
    echo "🔍 Verifying rollback..."
    
    sleep 60
    
    for i in {1..5}; do
        if curl -f "$api_url/health" &>/dev/null; then
            echo "✅ Health check passed (attempt $i)"
            break
        else
            echo "⚠️ Health check failed (attempt $i), retrying..."
            sleep 30
        fi
        
        if [ $i -eq 5 ]; then
            echo "❌ Rollback verification failed!"
            return 1
        fi
    done
    
    curl -f "$api_url/docs" &>/dev/null || {
        echo "❌ API docs not accessible after rollback"
        return 1
    }
    
    echo "✅ Rollback verification successful"
    return 0
}

# Function to notify about rollback
notify_rollback() {
    local status=$1
    local version=$2
    
    echo "📢 Sending rollback notification..."
    
    if [ -n "$SENTRY_DSN" ]; then
        python -c "
import sentry_sdk
sentry_sdk.init('$SENTRY_DSN')
sentry_sdk.capture_message(
    'Rollback $status to version $version',
    level='error' if '$status' == 'failed' else 'warning'
)
"
    fi
}

# Main execution
main() {
    echo "🚨 ROLLBACK INITIATED 🚨"
    echo "Environment: $ENVIRONMENT"
    echo "Target: $ROLLBACK_TARGET"
    
    if [ "$ROLLBACK_TARGET" = "previous" ]; then
        TARGET_VERSION=$(get_previous_version)
    else
        TARGET_VERSION=$ROLLBACK_TARGET
    fi
    
    if [ -z "$TARGET_VERSION" ]; then
        echo "❌ Could not determine target version for rollback"
        exit 1
    fi
    
    echo "Target version: $TARGET_VERSION"
    
    if [ -t 0 ]; then
        read -p "⚠️ Are you sure you want to rollback to $TARGET_VERSION? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "❌ Rollback cancelled"
            exit 1
        fi
    fi
    
    backup_current_state
    perform_rollback $TARGET_VERSION
    
    case $ENVIRONMENT in
        "production")
            API_URL=${PRODUCTION_API_URL:-"https://ai-agent-aff6.onrender.com"}
            ;;
        "staging")
            API_URL=${STAGING_API_URL:-"https://staging-ai-agent.onrender.com"}
            ;;
    esac
    
    if verify_rollback $API_URL; then
        echo "🎉 Rollback completed successfully!"
        notify_rollback "completed" $TARGET_VERSION
    else
        echo "❌ Rollback verification failed!"
        notify_rollback "failed" $TARGET_VERSION
        exit 1
    fi
}

main "$@"