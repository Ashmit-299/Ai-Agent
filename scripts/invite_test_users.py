#!/usr/bin/env python3
"""
Test User Invitation System
Creates test users and generates credentials for testing
"""

import os
import sys
import json
import time
import uuid
import hashlib
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

class TestUserInviter:
    def __init__(self):
        self.test_users = []
        self.credentials_file = "test_user_credentials.json"
        self.instructions_file = "testing_instructions.md"
        
    def create_test_user(self, username, email, role="user"):
        """Create a test user with credentials"""
        from ..app.security import hash_password
        
        user_id = f"test_{uuid.uuid4().hex[:8]}"
        password = f"test{username}123"
        password_hash = hash_password(password)
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "password": password,
            "password_hash": password_hash,
            "email": email,
            "role": role,
            "created_at": time.time(),
            "email_verified": True
        }
        
        return user_data
    
    def save_to_database(self, user_data):
        """Save user to database"""
        try:
            from ..core.database import DatabaseManager
            db = DatabaseManager()
            
            # Check if user already exists
            existing_user = db.get_user_by_username(user_data["username"])
            if existing_user:
                print(f"User {user_data['username']} already exists, skipping...")
                return False
            
            # Create user in database
            db_user_data = {
                "user_id": user_data["user_id"],
                "username": user_data["username"],
                "password_hash": user_data["password_hash"],
                "email": user_data["email"],
                "created_at": user_data["created_at"]
            }
            
            db.create_user(db_user_data)
            print(f"SUCCESS: Created user: {user_data['username']}")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to create user {user_data['username']}: {e}")
            return False
    
    def generate_test_users(self):
        """Generate standard test users"""
        test_user_configs = [
            {"username": "tester1", "email": "tester1@example.com", "role": "user"},
            {"username": "tester2", "email": "tester2@example.com", "role": "user"},
            {"username": "tester3", "email": "tester3@example.com", "role": "user"},
            {"username": "reviewer", "email": "reviewer@example.com", "role": "reviewer"},
            {"username": "admin_test", "email": "admin@example.com", "role": "admin"}
        ]
        
        print("Generating test users...")
        
        for config in test_user_configs:
            user_data = self.create_test_user(
                config["username"], 
                config["email"], 
                config["role"]
            )
            
            if self.save_to_database(user_data):
                self.test_users.append({
                    "username": user_data["username"],
                    "password": user_data["password"],
                    "email": user_data["email"],
                    "role": user_data["role"],
                    "user_id": user_data["user_id"]
                })
    
    def save_credentials(self):
        """Save test user credentials to file"""
        credentials = {
            "generated_at": datetime.now().isoformat(),
            "test_users": self.test_users,
            "api_base_url": "http://localhost:8000",
            "usage_instructions": [
                "1. Start the server: python start_server.py",
                "2. Use these credentials to login via POST /users/login",
                "3. Use the returned access_token for authenticated requests",
                "4. Test different user roles and permissions"
            ]
        }
        
        with open(self.credentials_file, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        print(f"SUCCESS: Credentials saved to {self.credentials_file}")
    
    def generate_testing_instructions(self):
        """Generate testing instructions markdown"""
        instructions = f"""# Testing Instructions

## Generated Test Users

| Username | Password | Email | Role |
|----------|----------|-------|------|
"""
        
        for user in self.test_users:
            instructions += f"| {user['username']} | {user['password']} | {user['email']} | {user['role']} |\n"
        
        instructions += f"""
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
curl -X POST "http://localhost:8000/users/login" \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=tester1&password=test1123"

# Use returned access_token for authenticated requests
curl -X GET "http://localhost:8000/users/profile" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. Content Upload Testing
```bash
# Upload content (requires authentication)
curl -X POST "http://localhost:8000/upload" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -F "file=@test_file.txt" \\
  -F "title=Test Content" \\
  -F "description=Test upload"
```

### 5. Feedback Testing
```bash
# Submit feedback (requires authentication)
curl -X POST "http://localhost:8000/feedback" \\
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{{"content_id": "CONTENT_ID", "rating": 4, "comment": "Great content!"}}'
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

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(self.instructions_file, 'w') as f:
            f.write(instructions)
        
        print(f"SUCCESS: Testing instructions saved to {self.instructions_file}")
    
    def cleanup_existing_test_users(self):
        """Remove existing test users"""
        try:
            from ..core.database import DatabaseManager
            from sqlmodel import Session, select, delete
            from ..core.models import User
            
            db = DatabaseManager()
            
            with Session(db.engine) as session:
                # Delete test users
                test_usernames = ['tester1', 'tester2', 'tester3', 'reviewer', 'admin_test']
                for username in test_usernames:
                    statement = delete(User).where(User.username == username)
                    session.exec(statement)
                
                session.commit()
                print("SUCCESS: Cleaned up existing test users")
                
        except Exception as e:
            print(f"WARNING: Cleanup warning: {e}")

def main():
    """Main invitation system"""
    print("Test User Invitation System")
    print("=" * 50)
    
    inviter = TestUserInviter()
    
    # Cleanup existing test users
    inviter.cleanup_existing_test_users()
    
    # Generate new test users
    inviter.generate_test_users()
    
    if inviter.test_users:
        # Save credentials and instructions
        inviter.save_credentials()
        inviter.generate_testing_instructions()
        
        print(f"\nSUCCESS: Successfully created {len(inviter.test_users)} test users")
        print(f"Credentials saved to: {inviter.credentials_file}")
        print(f"Instructions saved to: {inviter.instructions_file}")
        
        print("\nTest Users Created:")
        for user in inviter.test_users:
            print(f"  - {user['username']} ({user['role']}) - {user['email']}")
        
        print("\nNext Steps:")
        print("1. Start the server: python start_server.py")
        print("2. Follow testing instructions in testing_instructions.md")
        print("3. Use credentials from test_user_credentials.json")
        
    else:
        print("ERROR: No test users were created")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)