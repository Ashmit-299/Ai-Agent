# Testing Instructions

## Generated Test Users

| Username | Password | Email | Role |
|----------|----------|-------|------|
| tester1 | testtester1123 | tester1@example.com | user |
| tester2 | testtester2123 | tester2@example.com | user |
| tester3 | testtester3123 | tester3@example.com | user |
| reviewer | testreviewer123 | reviewer@example.com | reviewer |
| admin_test | testadmin_test123 | admin@example.com | admin |

## Testing Workflow

### 1. Start the Server
```bash
python start_server.py
```
Server will be available at: http://localhost:8000

### 2. API Documentation
Visit: http://localhost:8000/docs

### 3. Authentication Testing
```bash
# Login with test user
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=tester1&password=test1123"

# Use returned access_token for authenticated requests
curl -X GET "http://localhost:8000/users/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Content Upload Testing
```bash
# Upload content (requires authentication)
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@test_file.txt" \
  -F "title=Test Content" \
  -F "description=Test upload"
```

### 5. Feedback Testing
```bash
# Submit feedback (requires authentication)
curl -X POST "http://localhost:8000/feedback" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content_id": "CONTENT_ID", "rating": 4, "comment": "Great content!"}'
```

### 6. Role-Based Testing

#### Regular User (tester1, tester2, tester3)
- Can upload content
- Can submit feedback
- Can view own profile
- Cannot access admin endpoints

#### Reviewer (reviewer)
- All user permissions
- Can access analytics endpoints
- Can view system metrics

#### Admin (admin_test)
- All permissions
- Can access maintenance endpoints
- Can view system logs
- Can manage users

### 7. Test Scenarios

1. **Authentication Flow**
   - Register new user
   - Login with credentials
   - Access protected endpoints

2. **Content Management**
   - Upload various file types
   - Generate videos from scripts
   - Stream and download content

3. **AI Features**
   - Submit feedback for RL training
   - Get tag recommendations
   - View analytics data

4. **Security Testing**
   - Try accessing admin endpoints without proper role
   - Test rate limiting on invitation system
   - Verify input validation

### 8. Expected Results

- All test users should be able to login successfully
- Role-based access control should work correctly
- Content upload and feedback systems should function
- AI recommendations should improve with feedback
- Security measures should block unauthorized access

## Troubleshooting

If you encounter issues:
1. Check server logs for errors
2. Verify database connection
3. Ensure all dependencies are installed
4. Check environment variables are set correctly

Generated on: 2025-09-20 12:01:26
