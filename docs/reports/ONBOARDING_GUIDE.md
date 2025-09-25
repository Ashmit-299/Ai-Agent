# User Onboarding & Feedback Collection Guide

## Quick Start

### 1. Start the API Server
```bash
python start_server.py
# Server will be available at http://localhost:8000
```

### 2. Run User Onboarding Script
```bash
python scripts/onboard_users.py
```

This will:
- Register 5 test users automatically
- Test login functionality
- Simulate basic user activity
- Generate onboarding_results.json

### 3. Verify Onboarding
```bash
# Run integration tests
python -m pytest tests/integration/test_user_onboarding.py -v

# Check API documentation
# Visit: http://localhost:8000/docs
```

## Manual User Registration

### Via API
```bash
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "SecurePass@123",
    "email": "user@example.com"
  }'
```

### Via Swagger UI
1. Go to http://localhost:8000/docs
2. Find "STEP 2: User Authentication" section
3. Use `/users/register` endpoint
4. Fill in user details and execute

## Feedback Collection Process

### 1. User Journey Flow
```
Registration → Login → Upload Content → Generate Video → Submit Feedback
```

### 2. Collect Feedback via API
```bash
# Login first
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser1&password=Test@123"

# Use token for feedback
curl -X POST "http://localhost:8000/feedback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "content_123",
    "rating": 5,
    "comment": "Great content!"
  }'
```

### 3. Automated Feedback Collection
```bash
# Run the onboarding script which includes feedback simulation
python scripts/onboard_users.py

# Check feedback in analytics
curl "http://localhost:8000/bhiv/analytics"
```

## Observability & Monitoring

### PostHog Events
- **Event**: `request`
- **Properties**: `path`, `status`, `method`
- **Dashboard**: https://app.posthog.com

### Sentry Error Tracking
- **Automatic**: All exceptions captured
- **Dashboard**: https://sentry.io
- **Test**: `python test_observability.py`

### Test Observability
```bash
# Generate events and errors for testing
python test_observability.py
```

## User Onboarding Results

After running the onboarding script, check:

### 1. Registration Success
```json
{
  "success": true,
  "username": "testuser1",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user_id": "user_abc123"
}
```

### 2. Database Verification
```bash
# Check user count
curl "http://localhost:8000/metrics"

# Check analytics
curl "http://localhost:8000/bhiv/analytics"
```

### 3. Activity Simulation
The script automatically tests:
- User registration
- Login functionality  
- Content upload (if authenticated)
- Metrics access
- Basic API interaction

## Feedback Loop Integration

### 1. RL Agent Training
- Feedback automatically trains the Q-Learning agent
- Rating scale: 1-5 (maps to -1.0 to 1.0 reward)
- Agent learns content preferences over time

### 2. Tag Recommendations
- AI provides improved tag suggestions based on feedback
- Recommendations improve with more user interactions
- Access via `/recommend-tags/{content_id}`

### 3. Analytics Dashboard
- Real-time feedback metrics
- Sentiment analysis of comments
- User engagement tracking
- Access via `/bhiv/analytics`

## Troubleshooting

### Common Issues

**1. Server Not Running**
```bash
# Start server first
python start_server.py
```

**2. Database Connection Issues**
```bash
# Check environment variables
echo $DATABASE_URL
# Ensure PostgreSQL is accessible
```

**3. Authentication Errors**
```bash
# Verify Supabase configuration
echo $SUPABASE_PUBLIC_KEY
# Check JWT token format
```

### Verification Commands
```bash
# Health check
curl http://localhost:8000/health

# Test registration
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"Test@123","email":"test@test.com"}'

# Check metrics
curl http://localhost:8000/metrics
```

## Integration with CI/CD

The onboarding process is integrated with:
- **GitHub Actions**: Automated testing
- **PostHog**: Event tracking
- **Sentry**: Error monitoring
- **Database**: PostgreSQL with Supabase

For production deployment, ensure all environment variables are properly configured in your deployment platform.