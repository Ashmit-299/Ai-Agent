#!/usr/bin/env python3

import os
import re

def fix_streamlit_tests():
    """Fix streamlit test return warnings"""
    
    streamlit_test_path = "tests/unit/test_streamlit_fix.py"
    
    if not os.path.exists(streamlit_test_path):
        return
    
    with open(streamlit_test_path, 'r') as f:
        content = f.read()
    
    # Fix return statements in test functions
    content = re.sub(r'return True', 'assert True', content)
    content = re.sub(r'return False', 'assert False', content)
    
    with open(streamlit_test_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {streamlit_test_path}")

def fix_token_model_test():
    """Fix Token model test"""
    
    test_path = "tests/test_auth_security.py"
    
    with open(test_path, 'r') as f:
        content = f.read()
    
    # Fix Token model test
    old_token_test = '''    def test_token_model(self):
        """Test Token model"""
        token_data = {
            "access_token": "jwt_token_here",
            "token_type": "bearer",
            "user_id": "user123",
            "username": "testuser"
        }
        token = Token(**token_data)
        
        assert token.access_token == "jwt_token_here"
        assert token.token_type == "bearer"
        assert token.user_id == "user123"
        assert token.username == "testuser"'''
    
    new_token_test = '''    def test_token_model(self):
        """Test Token model"""
        token_data = {
            "access_token": "jwt_token_here",
            "refresh_token": "refresh_token_here",
            "token_type": "bearer",
            "expires_in": 1440,
            "user_id": "user123",
            "username": "testuser"
        }
        token = Token(**token_data)
        
        assert token.access_token == "jwt_token_here"
        assert token.refresh_token == "refresh_token_here"
        assert token.token_type == "bearer"
        assert token.expires_in == 1440
        assert token.user_id == "user123"
        assert token.username == "testuser"'''
    
    content = content.replace(old_token_test, new_token_test)
    
    with open(test_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed: Token model test")

def fix_bhiv_components_imports():
    """Fix BHIV components import errors"""
    
    test_files = [
        "tests/test_bhiv_components.py",
        "tests/unit/test_bhiv_components.py"
    ]
    
    for test_path in test_files:
        if not os.path.exists(test_path):
            continue
            
        with open(test_path, 'r') as f:
            content = f.read()
        
        # Fix import errors
        content = content.replace(
            "from app.auth import hash_password",
            "from app.security import PasswordManager"
        )
        content = content.replace(
            "from app.auth import verify_token",
            "from app.security import JWTManager"
        )
        content = content.replace(
            "hash_password(",
            "PasswordManager.hash_password("
        )
        content = content.replace(
            "verify_token(",
            "JWTManager.verify_token("
        )
        
        with open(test_path, 'w') as f:
            f.write(content)
        
        print(f"Fixed: {test_path}")

def create_minimal_test_config():
    """Create minimal test configuration"""
    
    pytest_ini = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
filterwarnings =
    ignore::DeprecationWarning
    ignore::PytestReturnNotNoneWarning
"""
    
    with open("pytest.ini", 'w') as f:
        f.write(pytest_ini)
    
    print("Created: pytest.ini")

def main():
    """Fix all test errors"""
    
    print("=== FIXING TEST ERRORS ===")
    
    fix_streamlit_tests()
    fix_token_model_test()
    fix_bhiv_components_imports()
    create_minimal_test_config()
    
    print("\nTest fixes completed!")

if __name__ == "__main__":
    main()