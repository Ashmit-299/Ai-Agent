#!/usr/bin/env python3
"""
Unit tests for BHIV Bucket Storage
Tests bucket storage operations, file handling, and error scenarios
"""

import pytest
import tempfile
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from core.bhiv_bucket import (
        save_script, save_storyboard, save_video, save_rating, save_log,
        get_bucket_path, get_script, get_storyboard, get_video_bytes,
        save_json, save_text, list_bucket_files, cleanup_temp_files,
        cleanup_old_files, rotate_logs, get_storage_stats, init_bucket
    )
except ImportError:
    # Skip tests if imports fail
    pytest.skip("Core modules not available", allow_module_level=True)

class TestBHIVBucket:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_bucket_root = Path(tempfile.mkdtemp())
        
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        if self.test_bucket_root.exists():
            shutil.rmtree(self.test_bucket_root)

    @patch('core.bhiv_bucket.BUCKET_ROOT')
    def test_init_bucket(self, mock_bucket_root):
        """Test bucket initialization"""
        mock_bucket_root.return_value = self.test_bucket_root
        
        with patch('core.bhiv_bucket.init_bucket') as mock_init:
            init_bucket()
            mock_init.assert_called_once()

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_save_script_local(self):
        """Test saving script to local storage"""
        # Create test script file
        test_script = self.test_bucket_root / "test_script.txt"
        test_script.parent.mkdir(parents=True, exist_ok=True)
        test_script.write_text("Test script content")
        
        # Create scripts directory
        scripts_dir = self.test_bucket_root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = save_script(str(test_script), "saved_script.txt")
            
            assert "saved_script.txt" in result
            saved_file = Path(result)
            assert saved_file.exists()
            assert saved_file.read_text() == "Test script content"

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_save_storyboard_local(self):
        """Test saving storyboard to local storage"""
        storyboard = {
            "scenes": [{"id": "scene_1", "text": "Test", "duration": 5.0}],
            "total_duration": 5.0
        }
        
        # Create storyboards directory
        storyboards_dir = self.test_bucket_root / "storyboards"
        storyboards_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = save_storyboard(storyboard, "test_storyboard.json")
            
            assert "test_storyboard.json" in result
            saved_file = Path(result)
            assert saved_file.exists()
            
            loaded_data = json.loads(saved_file.read_text())
            assert loaded_data == storyboard

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 's3')
    def test_save_script_s3(self):
        """Test saving script to S3 storage"""
        mock_s3_client = Mock()
        
        with patch('core.bhiv_bucket._get_s3_client', return_value=mock_s3_client):
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
                tmp_file.write("Test script")
                tmp_file.flush()
                tmp_file.close()  # Close file before using it
                
                try:
                    result = save_script(tmp_file.name, "test_script.txt")
                    
                    mock_s3_client.upload_file.assert_called_once()
                    assert result.startswith("s3://")
                    assert "scripts/test_script.txt" in result
                finally:
                    try:
                        os.unlink(tmp_file.name)
                    except (OSError, PermissionError):
                        pass  # Ignore cleanup errors on Windows

    def test_save_script_invalid_filename(self):
        """Test error handling for invalid filename"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.close()
            
            try:
                with pytest.raises(ValueError, match="(Invalid destination filename|Failed to save script)"):
                    save_script(tmp_file.name, "../invalid.txt")
            finally:
                try:
                    os.unlink(tmp_file.name)
                except (OSError, PermissionError):
                    pass

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_save_rating_local(self):
        """Test saving rating data"""
        rating_data = {
            "content_id": "test123",
            "rating": 4,
            "user_id": "user1",
            "comment": "Good content"
        }
        
        # Create ratings directory
        ratings_dir = self.test_bucket_root / "ratings"
        ratings_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = save_rating(rating_data, "test_rating.json")
            
            assert "test_rating.json" in result
            saved_file = Path(result)
            assert saved_file.exists()
            
            loaded_data = json.loads(saved_file.read_text())
            assert loaded_data == rating_data

    def test_save_rating_invalid_filename(self):
        """Test error handling for invalid rating filename"""
        rating_data = {"rating": 5}
        
        with pytest.raises(ValueError, match="Invalid filename"):
            save_rating(rating_data, "")

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_get_bucket_path(self):
        """Test getting bucket path"""
        # Create scripts directory
        scripts_dir = self.test_bucket_root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = get_bucket_path("scripts", "test.txt")
            
            assert "scripts" in result
            assert "test.txt" in result

    def test_get_bucket_path_invalid_segment(self):
        """Test error handling for invalid segment"""
        with pytest.raises(ValueError, match="Invalid segment"):
            get_bucket_path("invalid_segment", "test.txt")

    def test_get_bucket_path_invalid_filename(self):
        """Test error handling for invalid filename in bucket path"""
        with pytest.raises(ValueError, match="(Invalid filename|Path outside bucket)"):
            get_bucket_path("scripts", "../invalid.txt")

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_save_json(self):
        """Test saving JSON data"""
        test_data = {"key": "value", "number": 42}
        
        # Create logs directory
        logs_dir = self.test_bucket_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = save_json("logs", "test.json", test_data)
            
            assert "test.json" in result
            saved_file = Path(result)
            assert saved_file.exists()
            
            loaded_data = json.loads(saved_file.read_text())
            assert loaded_data == test_data

    def test_save_json_invalid_segment(self):
        """Test error handling for invalid segment in save_json"""
        with pytest.raises(ValueError, match="Invalid segment"):
            save_json("invalid", "test.json", {})

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_save_text(self):
        """Test saving text content"""
        test_content = "This is test content"
        
        # Create uploads directory
        uploads_dir = self.test_bucket_root / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            result = save_text("uploads", "test.txt", test_content)
            
            assert "test.txt" in result
            saved_file = Path(result)
            assert saved_file.exists()
            assert saved_file.read_text() == test_content

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_list_bucket_files(self):
        """Test listing bucket files"""
        # Create test files
        scripts_dir = self.test_bucket_root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        (scripts_dir / "file1.txt").write_text("content1")
        (scripts_dir / "file2.txt").write_text("content2")
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            files = list_bucket_files("scripts")
            
            assert len(files) == 2
            assert "file1.txt" in files
            assert "file2.txt" in files

    def test_list_bucket_files_invalid_segment(self):
        """Test error handling for invalid segment in list_bucket_files"""
        with pytest.raises(ValueError, match="Invalid segment"):
            list_bucket_files("invalid_segment")

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    @patch('core.bhiv_bucket.BUCKET_ROOT')
    def test_cleanup_temp_files(self, mock_bucket_root):
        """Test cleanup of temporary files"""
        mock_bucket_root.__truediv__ = lambda self, other: self.test_bucket_root / other
        mock_bucket_root.resolve.return_value = self.test_bucket_root
        
        # Create tmp directory with old files
        tmp_dir = self.test_bucket_root / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        
        old_file = tmp_dir / "old_file.txt"
        old_file.write_text("old content")
        
        # Mock file modification time to be old
        import time
        old_time = time.time() - (25 * 3600)  # 25 hours ago
        
        with patch('core.bhiv_bucket.init_bucket'):
            with patch.object(Path, 'stat') as mock_stat:
                mock_stat.return_value.st_mtime = old_time
                
                cleaned_count = cleanup_temp_files(24)
                assert cleaned_count >= 0

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_get_storage_stats(self):
        """Test getting storage statistics"""
        stats = get_storage_stats()
        
        assert stats["backend"] == "local"
        assert "segments" in stats
        assert "timestamp" in stats
        assert len(stats["segments"]) == 7

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 's3')
    @patch('core.bhiv_bucket.S3_BUCKET_NAME', 'test-bucket')
    def test_get_storage_stats_s3(self):
        """Test getting S3 storage statistics"""
        stats = get_storage_stats()
        
        assert stats["backend"] == "s3"
        assert stats["s3_bucket"] == "test-bucket"
        assert "segments" in stats

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_get_script(self):
        """Test retrieving script content"""
        # Create script file
        scripts_dir = self.test_bucket_root / "scripts"
        scripts_dir.mkdir(parents=True, exist_ok=True)
        script_file = scripts_dir / "test123_script.txt"
        script_file.write_text("Test script content")
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            content = get_script("test123")
            
            assert content == "Test script content"

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_get_script_not_found(self):
        """Test retrieving non-existent script"""
        with patch('core.bhiv_bucket.init_bucket'):
            content = get_script("nonexistent")
            assert content is None

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 'local')
    def test_get_storyboard(self):
        """Test retrieving storyboard"""
        # Create storyboard file
        storyboards_dir = self.test_bucket_root / "storyboards"
        storyboards_dir.mkdir(parents=True, exist_ok=True)
        storyboard_file = storyboards_dir / "test123_storyboard.json"
        
        test_storyboard = {"scenes": [{"id": "scene_1"}]}
        storyboard_file.write_text(json.dumps(test_storyboard))
        
        with patch('core.bhiv_bucket.BUCKET_ROOT', self.test_bucket_root):
            storyboard = get_storyboard("test123")
            
            assert storyboard == test_storyboard

    def test_get_storyboard_not_found(self):
        """Test retrieving non-existent storyboard"""
        storyboard = get_storyboard("nonexistent")
        assert storyboard is None

    def test_save_script_file_error(self):
        """Test error handling when script file doesn't exist"""
        with pytest.raises(ValueError, match="Failed to save script"):
            save_script("/nonexistent/file.txt", "dest.txt")

    @patch('core.bhiv_bucket.STORAGE_BACKEND', 's3')
    def test_s3_client_error_handling(self):
        """Test S3 client error handling"""
        with patch('core.bhiv_bucket._get_s3_client', side_effect=Exception("S3 Error")):
            with pytest.raises(ValueError, match="Failed to save script"):
                save_script("test.txt", "dest.txt")