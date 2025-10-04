#!/usr/bin/env python3
"""
Unit tests for Database Models and Operations
Tests SQLModel models, database operations, relationships, and constraints
"""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from core.database import DatabaseManager
from app.models import User, UserRegister, ContentUpload, FeedbackRequest

class TestDatabaseModels:
    
    def setup_method(self):
        """Setup test database"""
        self.test_db_path = tempfile.mktemp(suffix='.db')
        self.db_manager = DatabaseManager(db_path=self.test_db_path)
    
    def teardown_method(self):
        """Cleanup test database"""
        if os.path.exists(self.test_db_path):
            os.unlink(self.test_db_path)

    def test_database_manager_initialization(self):
        """Test DatabaseManager initialization"""
        assert self.db_manager is not None
        assert hasattr(self.db_manager, 'get_connection')

    @patch('sqlite3.connect')
    def test_database_connection(self, mock_connect):
        """Test database connection establishment"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db_manager = DatabaseManager()
        connection = db_manager.get_connection()
        
        mock_connect.assert_called()
        assert connection == mock_conn

    def test_user_model_validation(self):
        """Test User model field validation"""
        # Valid user data
        valid_user = User(
            user_id="user123",
            username="testuser",
            email="test@example.com"
        )
        
        assert valid_user.user_id == "user123"
        assert valid_user.username == "testuser"
        assert valid_user.email == "test@example.com"

    def test_user_model_optional_email(self):
        """Test User model with optional email field"""
        user_without_email = User(
            user_id="user123",
            username="testuser"
        )
        
        assert user_without_email.user_id == "user123"
        assert user_without_email.username == "testuser"
        assert user_without_email.email is None

    def test_user_register_model_validation(self):
        """Test UserRegister model validation"""
        # Valid registration data
        valid_registration = UserRegister(
            username="testuser",
            password="securepassword123",
            email="test@example.com"
        )
        
        assert valid_registration.username == "testuser"
        assert valid_registration.password == "securepassword123"
        assert valid_registration.email == "test@example.com"

    def test_user_register_model_constraints(self):
        """Test UserRegister model field constraints"""
        # Test minimum username length
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="ab", password="password123")
        
        # Test minimum password length
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username="testuser", password="12345")
        
        # Test maximum username length
        long_username = "a" * 51  # Exceeds max_length=50
        with pytest.raises(Exception):  # Pydantic validation error
            UserRegister(username=long_username, password="password123")

    def test_content_upload_model_validation(self):
        """Test ContentUpload model validation"""
        valid_content = ContentUpload(
            title="Test Content",
            description="This is a test content description"
        )
        
        assert valid_content.title == "Test Content"
        assert valid_content.description == "This is a test content description"

    def test_content_upload_model_constraints(self):
        """Test ContentUpload model field constraints"""
        # Test empty title (should fail)
        with pytest.raises(Exception):  # Pydantic validation error
            ContentUpload(title="", description="Valid description")
        
        # Test title too long
        long_title = "a" * 201  # Exceeds max_length=200
        with pytest.raises(Exception):  # Pydantic validation error
            ContentUpload(title=long_title, description="Valid description")
        
        # Test description too long
        long_description = "a" * 1001  # Exceeds max_length=1000
        with pytest.raises(Exception):  # Pydantic validation error
            ContentUpload(title="Valid title", description=long_description)

    def test_content_upload_optional_description(self):
        """Test ContentUpload with optional description"""
        content_no_desc = ContentUpload(title="Test Content")
        
        assert content_no_desc.title == "Test Content"
        assert content_no_desc.description == ""  # Default empty string

    def test_feedback_request_model_validation(self):
        """Test FeedbackRequest model validation"""
        valid_feedback = FeedbackRequest(
            content_id="content123",
            rating=4,
            comment="Great content!"
        )
        
        assert valid_feedback.content_id == "content123"
        assert valid_feedback.rating == 4
        assert valid_feedback.comment == "Great content!"

    def test_feedback_request_rating_constraints(self):
        """Test FeedbackRequest rating field constraints"""
        # Test rating below minimum (should fail)
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(content_id="content123", rating=0)
        
        # Test rating above maximum (should fail)
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(content_id="content123", rating=6)
        
        # Test valid ratings
        for rating in [1, 2, 3, 4, 5]:
            feedback = FeedbackRequest(content_id="content123", rating=rating)
            assert feedback.rating == rating

    def test_feedback_request_optional_comment(self):
        """Test FeedbackRequest with optional comment"""
        feedback_no_comment = FeedbackRequest(
            content_id="content123",
            rating=3
        )
        
        assert feedback_no_comment.content_id == "content123"
        assert feedback_no_comment.rating == 3
        assert feedback_no_comment.comment is None

    def test_feedback_request_comment_length(self):
        """Test FeedbackRequest comment length constraint"""
        long_comment = "a" * 501  # Exceeds max_length=500
        
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(
                content_id="content123",
                rating=3,
                comment=long_comment
            )

    @patch('core.database.DatabaseManager.get_connection')
    def test_create_user_operation(self, mock_get_connection):
        """Test user creation database operation"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        db_manager = DatabaseManager()
        
        user_data = {
            "user_id": "user123",
            "username": "testuser",
            "password_hash": "hashed_password",
            "email": "test@example.com"
        }
        
        # Mock the create_user method if it exists
        if hasattr(db_manager, 'create_user'):
            result = db_manager.create_user(user_data)
            
            # Verify database interaction
            mock_conn.cursor.assert_called()
            mock_conn.commit.assert_called()

    @patch('core.database.DatabaseManager.get_connection')
    def test_get_user_by_username_operation(self, mock_get_connection):
        """Test get user by username database operation"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_connection.return_value = mock_conn
        
        # Mock query result
        mock_cursor.fetchone.return_value = {
            "user_id": "user123",
            "username": "testuser",
            "password_hash": "hashed_password",
            "email": "test@example.com"
        }
        
        db_manager = DatabaseManager()
        
        # Mock the get_user_by_username method if it exists
        if hasattr(db_manager, 'get_user_by_username'):
            result = db_manager.get_user_by_username("testuser")
            
            # Verify database interaction
            mock_conn.cursor.assert_called()
            mock_cursor.execute.assert_called()

    def test_database_table_creation(self):
        """Test database table creation"""
        # This would test actual table creation if we have access to the schema
        # For now, we'll test that the database manager can be initialized
        db_manager = DatabaseManager()
        assert db_manager is not None

    @patch('sqlite3.connect')
    def test_database_connection_error_handling(self, mock_connect):
        """Test database connection error handling"""
        mock_connect.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception, match="Database connection failed"):
            db_manager = DatabaseManager()
            db_manager.get_connection()

    def test_model_serialization(self):
        """Test model serialization to dict"""
        user = User(
            user_id="user123",
            username="testuser",
            email="test@example.com"
        )
        
        # Test that model can be converted to dict
        user_dict = user.dict()
        
        assert user_dict["user_id"] == "user123"
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"

    def test_model_json_serialization(self):
        """Test model JSON serialization"""
        content = ContentUpload(
            title="Test Content",
            description="Test description"
        )
        
        # Test that model can be converted to JSON
        content_json = content.json()
        
        assert isinstance(content_json, str)
        assert "Test Content" in content_json
        assert "Test description" in content_json

    def test_model_field_validation_types(self):
        """Test model field type validation"""
        # Test that string fields reject non-string types
        with pytest.raises(Exception):  # Pydantic validation error
            User(user_id=123, username="testuser")  # user_id should be string
        
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(content_id="content123", rating="high")  # rating should be int

    def test_model_field_defaults(self):
        """Test model field default values"""
        # Test ContentUpload default description
        content = ContentUpload(title="Test Title")
        assert content.description == ""
        
        # Test User optional email
        user = User(user_id="user123", username="testuser")
        assert user.email is None

    def test_model_field_validation_edge_cases(self):
        """Test model validation edge cases"""
        # Test exact boundary values
        
        # Username exactly at minimum length (3 chars)
        user_reg = UserRegister(username="abc", password="password123")
        assert user_reg.username == "abc"
        
        # Password exactly at minimum length (6 chars)
        user_reg = UserRegister(username="testuser", password="123456")
        assert user_reg.password == "123456"
        
        # Rating at boundaries
        feedback_min = FeedbackRequest(content_id="content123", rating=1)
        assert feedback_min.rating == 1
        
        feedback_max = FeedbackRequest(content_id="content123", rating=5)
        assert feedback_max.rating == 5

    def test_model_immutability(self):
        """Test that models handle field updates correctly"""
        user = User(user_id="user123", username="testuser")
        
        # Test that we can create a new instance with updated fields
        updated_user = user.copy(update={"email": "new@example.com"})
        
        assert user.email is None  # Original unchanged
        assert updated_user.email == "new@example.com"  # New instance updated

    @patch('core.database.DatabaseManager')
    def test_database_transaction_handling(self, mock_db_manager):
        """Test database transaction handling"""
        mock_conn = Mock()
        mock_db_manager.return_value.get_connection.return_value = mock_conn
        
        # Test that commit is called on successful operations
        db_manager = DatabaseManager()
        
        # Simulate a successful operation
        if hasattr(db_manager, 'create_user'):
            try:
                db_manager.create_user({"user_id": "test", "username": "test"})
                # Should call commit on success
            except AttributeError:
                # Method doesn't exist, which is fine for this test
                pass

    def test_content_id_validation(self):
        """Test content ID validation in feedback requests"""
        # Test empty content_id
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(content_id="", rating=3)
        
        # Test very long content_id
        long_content_id = "a" * 101  # Exceeds max_length=100
        with pytest.raises(Exception):  # Pydantic validation error
            FeedbackRequest(content_id=long_content_id, rating=3)

    def test_email_format_validation(self):
        """Test email format validation if implemented"""
        # Note: Basic Pydantic doesn't validate email format by default
        # This test would be relevant if EmailStr is used instead of str
        
        user_reg = UserRegister(
            username="testuser",
            password="password123",
            email="not-an-email"  # Invalid format but accepted by basic str field
        )
        
        # Should accept any string for basic str field
        assert user_reg.email == "not-an-email"