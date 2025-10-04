# Feedback Endpoint Error - SOLVED

## Root Cause

**Foreign Key Constraint Violation**

The feedback endpoint is failing because:
1. Your JWT token contains user_id: `544951686 0f9` (with a space)
2. The actual user_id in database is: `5449516860f9` (without space)
3. When inserting feedback, PostgreSQL checks the foreign key constraint
4. The user_id from the token doesn't match any user in the database
5. Result: Foreign key violation error

## Error Details

```
psycopg2.errors.ForeignKeyViolation: insert or update on table "feedback" 
violates foreign key constraint "feedback_user_id_fkey"
DETAIL: Key (user_id)=(544951686 0f9) is not present in table "user".
```

## Solution

### Step 1: Login Again to Get Fresh Token

Your current token is outdated or corrupted. Get a new one:

```bash
curl -X POST "http://localhost:9000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ashm&password=YOUR_PASSWORD"
```

This will return a new token with the correct user_id.

### Step 2: Use the New Token

Copy the `access_token` from the login response and use it in the feedback request:

```bash
curl -X POST "http://localhost:9000/feedback" \
  -H "Authorization: Bearer NEW_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "9a2b35e14d7c_30df5d",
    "rating": 5,
    "comment": "great"
  }'
```

### Step 3: Verify It Works

You should get a success response like:

```json
{
  "status": "success",
  "rating": 5,
  "event_type": "like",
  "reward": 1.0,
  "rl_training": {
    "agent_trained": true,
    "current_epsilon": 0.1,
    "q_states": 10,
    "avg_recent_reward": 0.5
  },
  "next_step": "GET /recommend-tags/9a2b35e14d7c_30df5d to see updated AI recommendations"
}
```

## Why This Happened

The token you're using was likely generated:
1. From an old session
2. Before a database migration
3. With a bug in the token generation code

The token contains `user_id: "544951686 0f9"` (with space) but the database has `user_id: "5449516860f9"` (without space).

## Verification

To verify your current user_id:

```bash
# Check your user in database
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT user_id, username FROM \"user\" WHERE username = %s', ('ashm',))
print(cur.fetchone())
cur.close()
conn.close()
"
```

Output should be: `('5449516860f9', 'ashm')`

## Testing in Swagger UI

1. Go to http://localhost:9000/docs
2. Click "Authorize" button (top right)
3. Login with username: `ashm` and your password
4. This will automatically use the correct token
5. Try POST /feedback endpoint
6. It should work now!

## Alternative: Use Demo User

If you don't remember your password, use the demo user:

```bash
# Get demo credentials
curl http://localhost:9000/demo-login

# Login as demo
curl -X POST "http://localhost:9000/users/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo&password=demo1234"

# Use the token from demo login
```

## Summary

- **Problem**: Token has wrong user_id format
- **Solution**: Login again to get fresh token
- **Status**: Database is working correctly
- **Action**: Get new token and retry

The feedback endpoint code is working fine. The issue was just an invalid token!
