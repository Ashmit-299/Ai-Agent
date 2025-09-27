# Supabase Database Integration Guide

## Overview

Your AI-Agent project now has **complete integration** with all Supabase tables:
- ✅ **user** - User accounts and authentication
- ✅ **content** - Uploaded files and media
- ✅ **script** - Text scripts and video generation content
- ✅ **videos** - Video-specific metadata and processing info
- ✅ **feedback** - User ratings and comments
- ✅ **analytics** - Event tracking and user behavior
- ✅ **system_logs** - Application logs and monitoring
- ✅ **alembic_version** - Database migration tracking

## Database Schema Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                    Supabase Database Schema                     │
├─────────────────────────────────────────────────────────────────┤
│  👤 user                                                        │
│  ├── user_id (PK)                                              │
│  ├── username, email, password_hash                            │
│  └── created_at, last_login, role                              │
│                                                                 │
│  📁 content                                                     │
│  ├── content_id (PK)                                           │
│  ├── uploader_id → user.user_id (FK)                          │
│  ├── title, description, file_path                             │
│  └── views, likes, shares, authenticity_score                  │
│                                                                 │
│  📝 script                                                      │
│  ├── script_id (PK)                                            │
│  ├── content_id → content.content_id (FK)                     │
│  ├── user_id → user.user_id (FK)                              │
│  └── script_content, script_type, used_for_generation          │
│                                                                 │
│  🎬 videos                                                      │
│  ├── video_id (PK)                                             │
│  ├── content_id → content.content_id (FK)                     │
│  ├── script_id → script.script_id (FK)                        │
│  └── duration, resolution, processing_status                   │
│                                                                 │
│  💬 feedback                                                    │
│  ├── id (PK)                                                   │
│  ├── content_id → content.content_id (FK)                     │
│  ├── user_id → user.user_id (FK)                              │
│  └── rating, comment, sentiment, engagement_score              │
│                                                                 │
│  📊 analytics                                                   │
│  ├── id (PK)                                                   │
│  ├── user_id → user.user_id (FK)                              │
│  ├── content_id → content.content_id (FK)                     │
│  └── event_type, event_data, timestamp                         │
│                                                                 │
│  📋 system_logs                                                 │
│  ├── id (PK)                                                   │
│  ├── user_id → user.user_id (FK)                              │
│  └── level, message, module, timestamp                         │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Features

### 1. Enhanced Database Operations
- **Relationship Management**: Automatic foreign key handling
- **Analytics Tracking**: Every operation logs analytics events
- **System Logging**: Comprehensive audit trail
- **Data Integrity**: Cascading deletes and referential integrity

### 2. New API Endpoints

#### Content with Relationships
```bash
GET /content/{content_id}/metadata
# Returns content with related scripts, feedback stats, and analytics
```

#### User Statistics
```bash
GET /users/{user_id}/stats
# Returns user with content count, script count, feedback given
```

#### Comprehensive Analytics
```bash
GET /bhiv/analytics
# Enhanced analytics with sentiment analysis and engagement metrics
```

#### System Health
```bash
GET /observability/health
# System health metrics from integrated logs and analytics
```

### 3. Database Integration Module

Located at `core/database_integration.py`:

```python
from core.database_integration import db_integration

# Create user with automatic analytics logging
user = db_integration.create_user_with_analytics(user_data)

# Create content with script relationship
result = db_integration.create_content_with_relationships(content_data, script_data)

# Get comprehensive content details
details = db_integration.get_content_with_relationships(content_id)

# Get dashboard data from all tables
dashboard = db_integration.get_dashboard_data()
```

## Running Integration Tests

### Quick Test
```bash
python scripts/integration/run_integration_test.py
```

### Detailed Test
```bash
python scripts/integration/connect_all_tables.py
```

### Migration Update
```bash
python scripts/migration/run_migrations.py upgrade
```

## Integration Status

### ✅ Completed Integrations

1. **User Management**
   - User creation with analytics logging
   - User statistics with related data counts
   - Authentication with system logging

2. **Content Management**
   - Content upload with script linking
   - Comprehensive metadata retrieval
   - View/like/share tracking

3. **Script Management**
   - Script creation with content association
   - Video generation script tracking
   - User script history

4. **Feedback System**
   - Feedback with sentiment analysis
   - Content rating aggregation
   - User engagement scoring

5. **Analytics Engine**
   - Event tracking for all operations
   - User behavior analysis
   - Content performance metrics

6. **System Monitoring**
   - Comprehensive logging
   - Health metrics calculation
   - Error tracking and alerting

### 🔄 Automatic Operations

- **Analytics Logging**: Every user action automatically logged
- **System Logging**: All operations create audit trail entries
- **Relationship Management**: Foreign keys automatically maintained
- **Data Validation**: Input sanitization and validation
- **Performance Tracking**: Operation timing and metrics

## API Usage Examples

### 1. Upload Content with Script
```python
# Upload file creates content AND script entries
POST /upload
{
    "file": "script.txt",
    "title": "My Video Script",
    "description": "Script for video generation"
}
# Automatically creates entries in content AND script tables
```

### 2. Generate Video from Script
```python
# Video generation links content, script, and videos tables
POST /generate-video
{
    "file": "script.txt",
    "title": "Generated Video"
}
# Creates entries in content, script, AND videos tables
```

### 3. Submit Feedback
```python
# Feedback automatically updates analytics
POST /feedback
{
    "content_id": "abc123",
    "rating": 5,
    "comment": "Great content!"
}
# Creates feedback entry AND analytics event AND system log
```

### 4. Get Comprehensive Analytics
```python
# Single endpoint returns data from all tables
GET /bhiv/analytics
# Returns integrated data from users, content, feedback, analytics tables
```

## Dashboard Integration

Your dashboard at `/dashboard` now shows:
- **Total Users**: From user table
- **Total Content**: From content table  
- **Total Scripts**: From script table
- **Total Feedback**: From feedback table
- **System Health**: From system_logs table
- **Recent Activity**: From analytics table

## Monitoring and Observability

### System Health Endpoints
- `/observability/health` - Overall system health
- `/observability/performance` - Performance metrics
- `/logs?admin_key=logs_2025` - System logs (admin only)

### Analytics Endpoints
- `/metrics` - System and RL agent metrics
- `/bhiv/analytics` - Comprehensive analytics
- `/reports/video-stats` - Video-specific statistics

## Database Maintenance

### Automated Cleanup
```python
# Clean old analytics data (90+ days)
cleanup_count = db_integration.cleanup_old_analytics(days_to_keep=90)

# Get database statistics
stats = db_integration.get_database_stats()
```

### Health Monitoring
```python
# Get system health from logs
health = db_integration.get_system_health_metrics()

# Monitor error rates and system status
dashboard_data = db_integration.get_dashboard_data()
```

## Next Steps

1. **Test Integration**: Run `python scripts/integration/run_integration_test.py`
2. **Check Dashboard**: Visit `/dashboard` to see integrated data
3. **Monitor Health**: Use `/observability/health` for system status
4. **View Analytics**: Check `/bhiv/analytics` for comprehensive metrics

Your Supabase database is now **fully integrated** with comprehensive relationships, analytics tracking, and system monitoring! 🎉