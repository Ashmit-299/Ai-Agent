# Production Deployment Guide

## 🚀 STEP 3: Deployment Verification (1-2 hours)

### Prerequisites
- Render.com account
- Perplexity API key
- Supabase database configured

### 1. Deploy to Render.com

#### Option A: Manual Deployment
1. Go to [Render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repository
4. Use these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.9+

#### Option B: Using render.yaml
1. Push your code to GitHub
2. In Render dashboard, create "New Blueprint"
3. Connect repository and deploy using `docker/render.yaml`

### 2. Configure Environment Variables

Add these environment variables in Render dashboard:

```bash
JWS_SECRET=<your-jws-secret-key>
DATABASE_URL=postgresql://<username>:<password>@<host>:<port>/<database>
POSTHOG_API_KEY=<your-posthog-api-key>
SENTRY_DSN=<your-sentry-dsn>
JWT_SECRET_KEY=<your-jwt-secret-key>
PERPLEXITY_API_KEY=<your-perplexity-api-key>
BHIV_LM_URL=https://api.perplexity.ai
BHIV_STORAGE_BACKEND=local
```

### 3. Configure LLM Service (Perplexity API)

```bash
python scripts/configure_llm_production.py
```

This script will:
- Validate your Perplexity API key
- Test storyboard generation
- Generate configuration report

### 4. Verify Deployment

```bash
python deploy_to_render.py
```

This script will:
- Test health endpoints
- Verify API functionality
- Test user authentication flow
- Monitor performance

### 5. Test with 5-10 Users

```bash
python scripts/production_test.py
```

This script will:
- Create 5-10 test users concurrently
- Test complete user workflows
- Upload content and submit feedback
- Generate test report

### 6. Monitor Production

```bash
python scripts/monitor_production.py
```

This script will:
- Monitor application health
- Track performance metrics
- Check database connectivity
- Generate monitoring reports

## 📊 Expected Results

### Deployment Success Criteria
- ✅ Health endpoint returns 200
- ✅ API endpoints respond correctly
- ✅ User authentication works
- ✅ Database connectivity confirmed
- ✅ 90%+ uptime during monitoring

### User Testing Success Criteria
- ✅ 80%+ user registration success
- ✅ 70%+ content upload success
- ✅ 60%+ feedback submission success
- ✅ Response times < 3 seconds

### Performance Benchmarks
- ✅ Average response time < 2 seconds
- ✅ Error rate < 5%
- ✅ Concurrent user support (5-10 users)
- ✅ Database query performance

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify Supabase credentials
   - Check IPv4 connection string
   - Test with `python test_db_connection.py`

2. **LLM Service Errors**
   - Validate Perplexity API key
   - Check API rate limits
   - Test with `python scripts/configure_llm_production.py`

3. **Deployment Failures**
   - Check build logs in Render dashboard
   - Verify requirements.txt dependencies
   - Check environment variables

4. **Performance Issues**
   - Monitor with `python scripts/monitor_production.py`
   - Check database query performance
   - Review error logs

## 📋 Deployment Checklist

- [ ] Render.com service created
- [ ] Environment variables configured
- [ ] Perplexity API key validated
- [ ] Health check passes
- [ ] API endpoints tested
- [ ] User workflow verified
- [ ] 5-10 user test completed
- [ ] Performance monitoring active
- [ ] Error tracking configured
- [ ] Deployment report generated

## 🎉 Success Confirmation

Your deployment is successful when:
1. All scripts run without errors
2. Test reports show >80% success rates
3. Monitoring shows stable performance
4. Users can complete full workflows

## 📞 Support

If you encounter issues:
1. Check the generated reports in project directory
2. Review Render.com deployment logs
3. Test individual components with provided scripts
4. Verify all environment variables are set correctly