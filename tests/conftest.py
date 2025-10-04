import pytest
import os
import sys
import tempfile
import asyncio
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_env():
    """Mock environment variables for testing"""
    return {
        "DATABASE_URL": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key",
        "PERPLEXITY_API_KEY": "test-api-key",
        "BHIV_LM_URL": "http://localhost:8001",
        "BHIV_LM_API_KEY": "test_api_key",
        "BHIV_STORAGE_BACKEND": "local",
        "BHIV_BUCKET_PATH": "test_bucket"
    }

@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return Mock()

@pytest.fixture
def temp_bucket_path():
    """Create temporary bucket path for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def sample_script_content():
    """Sample script content for testing"""
    return "This is a test script for video generation\nScene 1: Introduction\nScene 2: Main content"

@pytest.fixture
def sample_storyboard():
    """Sample storyboard for testing"""
    return {
        "version": "1.0",
        "total_duration": 10.0,
        "scenes": [
            {
                "id": "scene_1",
                "start_time": 0,
                "duration": 5.0,
                "frames": [
                    {
                        "id": "frame_1_1",
                        "text": "Test scene content",
                        "text_position": "center"
                    }
                ]
            }
        ]
    }

@pytest.fixture
def mock_database_connection():
    """Mock database connection"""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    return mock_conn

@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch, mock_env):
    """Setup test environment variables"""
    for key, value in mock_env.items():
        monkeypatch.setenv(key, value)

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing"""
    mock_client = Mock()
    mock_client.upload_file.return_value = None
    mock_client.put_object.return_value = None
    mock_client.get_object.return_value = {
        'Body': Mock(read=Mock(return_value=b'test content'))
    }
    mock_client.list_objects_v2.return_value = {'Contents': []}
    return mock_client

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response"""
    return {
        "scenes": [
            {
                "id": "scene_1",
                "text": "LLM generated scene",
                "duration": 5.0
            }
        ],
        "total_duration": 5.0,
        "version": "1.0",
        "llm_enhanced": True
    }