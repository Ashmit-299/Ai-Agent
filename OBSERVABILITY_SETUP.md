# PostHog & Sentry Integration Setup Guide

Your project already has comprehensive observability integration! Here's how to configure it:

## 🚀 Quick Setup

### 1. Get Your Credentials

**Sentry (Error Tracking):**
- Go to [sentry.io](https://sentry.io)
- Create account/login
- Create new project → Select "FastAPI"
- Copy your DSN from Project Settings

**PostHog (Analytics):**
- Go to [posthog.com](https://posthog.com)
- Create account/login
- Copy your Project API Key from Project Settings

### 2. Update Your .env File

```bash
# Copy example file
cp .env.example .env

# Edit .env with your credentials
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
POSTHOG_API_KEY=phc_your-posthog-api-key
POSTHOG_HOST=https://us.posthog.com
ENVIRONMENT=development
```

### 3. Verify Integration

Start your server and check:
```bash
python scripts/start_server.py

# Check observability status
curl http://localhost:8000/health/detailed
```

## 📊 What's Already Integrated

### Sentry Features
✅ **Automatic error capture** - All exceptions sent to Sentry  
✅ **Performance monitoring** - API response times tracked  
✅ **User context** - User info attached to errors  
✅ **Custom error filtering** - Filters out expected errors  
✅ **Environment tagging** - Separates dev/prod errors  

### PostHog Features
✅ **User event tracking** - Login, uploads, feedback tracked  
✅ **Feature usage analytics** - Track which features are used  
✅ **Performance metrics** - Response times and success rates  
✅ **User identification** - Link events to specific users  
✅ **Custom properties** - Rich event metadata  

### Built-in Decorators
```python
from app.observability import track_performance, track_user_action

@track_performance("video_generation")
@track_user_action("generate_video")
async def generate_video(user_id: str):
    # Your code here
    pass
```

## 🔍 Monitoring Your App

### Sentry Dashboard
- **Errors**: Real-time error tracking with stack traces
- **Performance**: API endpoint response times
- **Releases**: Track deployments and error rates

### PostHog Dashboard
- **Events**: User actions and feature usage
- **Funnels**: User journey analysis
- **Retention**: User engagement metrics

## 🛠️ Advanced Configuration

### Custom Event Tracking
```python
from app.observability import track_event, capture_exception

# Track custom events
track_event(user_id="user123", event="video_shared", properties={
    "video_id": "vid123",
    "platform": "twitter"
})

# Capture custom errors
try:
    risky_operation()
except Exception as e:
    capture_exception(e, {"context": "video_processing"})
```

### Environment-Specific Settings
```bash
# Development
SENTRY_TRACES_SAMPLE_RATE=1.0  # Track all requests
POSTHOG_ENABLED=true

# Production  
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of requests
POSTHOG_ENABLED=true
```

## 🚨 Troubleshooting

### Sentry Not Working?
1. Check DSN format: `https://key@sentry.io/project-id`
2. Verify environment: `ENVIRONMENT=development`
3. Check logs: Look for "Sentry initialized successfully"

### PostHog Not Working?
1. Check API key format: `phc_...`
2. Verify host: `https://us.posthog.com` or `https://eu.posthog.com`
3. Check logs: Look for "PostHog initialized successfully"

### Test Integration
```bash
# Trigger test error
curl -X POST http://localhost:8000/test-error

# Check observability health
curl http://localhost:8000/health/detailed
```

## 📈 Monitoring Checklist

- [ ] Sentry DSN configured
- [ ] PostHog API key configured  
- [ ] Environment variables set
- [ ] Server starts without errors
- [ ] Health check shows observability enabled
- [ ] Test events appear in dashboards

Your observability stack is production-ready! 🎉