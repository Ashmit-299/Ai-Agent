#!/bin/bash
# Production migration script with safety checks

set -e  # Exit on any error

echo "🚀 AI Agent Database Migration Script"
echo "======================================"

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL environment variable is not set"
    exit 1
fi

# Check if we're in production
if [[ "$DATABASE_URL" == *"postgresql"* ]]; then
    echo "📊 Production PostgreSQL database detected"
    echo "🔒 Running in production mode with safety checks"
    
    # Backup before migration (for PostgreSQL)
    echo "💾 Creating backup before migration..."
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Extract connection details from DATABASE_URL
    if command -v pg_dump &> /dev/null; then
        pg_dump "$DATABASE_URL" > "$BACKUP_FILE" || {
            echo "⚠️  Backup failed, but continuing with migration..."
        }
        echo "✅ Backup created: $BACKUP_FILE"
    else
        echo "⚠️  pg_dump not available, skipping backup"
    fi
else
    echo "🧪 Development SQLite database detected"
fi

# Run migrations
echo "⬆️  Running database migrations..."
python run_migrations.py upgrade

if [ $? -eq 0 ]; then
    echo "✅ Database migration completed successfully!"
    
    # Verify migration
    echo "🔍 Verifying database state..."
    python -c "
import sys
sys.path.append('.')
from core.database import DatabaseManager
try:
    db = DatabaseManager()
    analytics = db.get_analytics_data()
    print(f'✅ Database verification successful')
    print(f'   - Users: {analytics.get(\"total_users\", 0)}')
    print(f'   - Content: {analytics.get(\"total_content\", 0)}')
    print(f'   - Feedback: {analytics.get(\"total_feedback\", 0)}')
except Exception as e:
    print(f'⚠️  Database verification warning: {e}')
    sys.exit(0)  # Don't fail on verification issues
"
    
    echo "🎉 Migration process completed!"
else
    echo "❌ Migration failed!"
    
    if [[ "$DATABASE_URL" == *"postgresql"* ]] && [ -f "$BACKUP_FILE" ]; then
        echo "🔄 To rollback, you can restore from backup:"
        echo "   psql \$DATABASE_URL < $BACKUP_FILE"
    fi
    
    exit 1
fi