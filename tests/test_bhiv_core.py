#!/usr/bin/env python3
"""
Unit tests for BHIV Core Orchestrator
Tests process_script_upload, webhook processing, rating system, and async operations
"""

import pytest
import asyncio
import tempfile
import json
import os
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from core.bhiv_core import (
    process_script_upload_async, process_script_upload, process_webhook_ingest,
    notify_on_rate, regenerate_video, get_content_metadata, log_processing_event,
    _extract_script_from_payload, _get_db_conn
)

class TestBHIVCore:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_content_id = "test123"
        self.test_script_content = "This is a test script for video generation"
    
    @pytest.mark.asyncio
    async def test_process_script_upload_async_success(self):
        """Test async script upload processing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(self.test_script_content)
            tmp_file.flush()
            
            try:
                result = await process_script_upload_async(
                    file_path=tmp_file.name,
                    uploader="test_user"
                )
                
                assert result["status"] == "enqueued"
                assert "job_id" in result
                
            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_process_script_upload_async_no_input(self):
        """Test async script upload with no input"""
        result = await process_script_upload_async()
        
        assert result["status"] == "error"
        assert result["reason"] == "no_input"

    @pytest.mark.asyncio
    async def test_process_script_upload_async_with_text(self):
        """Test async script upload with script text"""
        result = await process_script_upload_async(
            script_text=self.test_script_content,
            uploader="test_user"
        )
        
        assert result["status"] == "enqueued"
        assert "job_id" in result

    @pytest.mark.asyncio
    @patch('core.bhiv_core.save_script')
    @patch('core.bhiv_core.save_storyboard')
    @patch('core.bhiv_core.render_video_from_storyboard')
    @patch('core.bhiv_core.bhiv_lm_client.suggest_storyboard')
    async def test_process_script_upload_success(self, mock_suggest, mock_render, mock_save_sb, mock_save_script):
        """Test successful script upload processing"""
        # Setup mocks
        mock_save_script.return_value = "/bucket/scripts/test_script.txt"
        mock_save_sb.return_value = "/bucket/storyboards/test_storyboard.json"
        mock_render.return_value = "/bucket/videos/test.mp4"
        mock_suggest.return_value = {
            "scenes": [{"id": "scene_1", "text": "Test scene", "duration": 5.0}],
            "total_duration": 5.0,
            "version": "1.0"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(self.test_script_content)
            tmp_file.flush()
            
            try:
                result = await process_script_upload(tmp_file.name, "test_user", "Test Title")
                
                assert result["processing_status"] == "completed"
                assert "content_id" in result
                assert result["uploader_id"] == "test_user"
                assert result["title"] == "Test Title"
                assert "paths" in result
                
                # Verify all save operations were called
                mock_save_script.assert_called_once()
                mock_save_sb.assert_called_once()
                mock_render.assert_called_once()
                
            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    @patch('core.bhiv_core.save_script')
    @patch('core.bhiv_core.bhiv_lm_client.suggest_storyboard')
    async def test_process_script_upload_llm_fallback(self, mock_suggest, mock_save_script):
        """Test script upload with LLM fallback"""
        mock_save_script.return_value = "/bucket/scripts/test_script.txt"
        mock_suggest.side_effect = Exception("LLM service unavailable")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(self.test_script_content)
            tmp_file.flush()
            
            try:
                with patch('video.storyboard.generate_storyboard_from_text') as mock_fallback:
                    mock_fallback.return_value = {
                        "scenes": [{"id": "scene_1", "duration": 5.0}],
                        "total_duration": 5.0
                    }
                    
                    with patch('core.bhiv_core.render_video_from_storyboard') as mock_render:
                        mock_render.return_value = "/bucket/videos/test.mp4"
                        
                        result = await process_script_upload(tmp_file.name, "test_user")
                        
                        assert result["processing_status"] == "completed"
                        mock_fallback.assert_called_once()
                        
            finally:
                os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_process_webhook_ingest_with_script_text(self):
        """Test webhook ingestion with script text"""
        payload = {
            "script": "This is a webhook script",
            "source": "external_api"
        }
        
        with patch('core.bhiv_core.save_json') as mock_save_json:
            with patch('core.bhiv_core.save_text') as mock_save_text:
                with patch('core.bhiv_core.process_script_upload') as mock_process:
                    mock_process.return_value = {"status": "completed"}
                    
                    result = await process_webhook_ingest(payload=payload)
                    
                    assert result["status"] == "ok"
                    assert "content_id" in result
                    assert result["note"] == "pipeline_invoked"

    @pytest.mark.asyncio
    async def test_process_webhook_ingest_no_script(self):
        """Test webhook ingestion without script content"""
        payload = {
            "metadata": {"type": "unknown"},
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        result = await process_webhook_ingest(payload=payload)
        
        assert result["status"] == "error"
        assert result["reason"] == "no_script_found"
        assert "raw_id" in result

    @pytest.mark.asyncio
    async def test_process_webhook_ingest_with_url(self):
        """Test webhook ingestion with URL fallback"""
        payload = {
            "url": "https://example.com/content",
            "metadata": {"type": "video"}
        }
        
        with patch('core.bhiv_core.save_json') as mock_save_json:
            with patch('core.bhiv_core.save_text') as mock_save_text:
                with patch('core.bhiv_core.process_script_upload') as mock_process:
                    mock_process.return_value = {"status": "completed"}
                    
                    result = await process_webhook_ingest(payload=payload)
                    
                    assert result["status"] == "ok"
                    assert "content_id" in result

    def test_extract_script_from_payload_direct(self):
        """Test script extraction from payload - direct fields"""
        payload = {"script": "Direct script content"}
        result = _extract_script_from_payload(payload)
        assert result == "Direct script content"
        
        payload = {"text": "Text content"}
        result = _extract_script_from_payload(payload)
        assert result == "Text content"

    def test_extract_script_from_payload_nested(self):
        """Test script extraction from nested payload"""
        payload = {
            "data": {
                "script": "Nested script content"
            }
        }
        result = _extract_script_from_payload(payload)
        assert result == "Nested script content"

    def test_extract_script_from_payload_fallback(self):
        """Test script extraction fallback to first string field"""
        payload = {
            "random_field": "Some content that is long enough",
            "number": 123
        }
        result = _extract_script_from_payload(payload)
        assert result == "Some content that is long enough"

    def test_extract_script_from_payload_none(self):
        """Test script extraction returns None for empty payload"""
        assert _extract_script_from_payload(None) is None
        assert _extract_script_from_payload({}) is None
        assert _extract_script_from_payload({"number": 123}) is None

    @patch('core.bhiv_core._get_db_conn')
    def test_notify_on_rate_success(self, mock_get_conn):
        """Test rating notification processing"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"avg_rating": 3.5, "cnt": 2}
        mock_get_conn.return_value = mock_conn
        
        rating_payload = {
            "rating": 4,
            "user_id": "user123",
            "comment": "Great content!"
        }
        
        with patch('core.bhiv_core.save_rating') as mock_save_rating:
            with patch('core.bhiv_core.bhiv_lm_client.improve_storyboard') as mock_improve:
                # Mock async function to return a coroutine
                async def mock_coro():
                    return {"improvement_applied": True}
                mock_improve.return_value = mock_coro()
                
                result = notify_on_rate(self.test_content_id, rating_payload)
                
                assert result["status"] == "ok"
                assert result["rating"] == 4
                assert result["avg_rating"] == 3.5
                assert result["count"] == 2
                mock_save_rating.assert_called_once()

    @patch('core.bhiv_core._get_db_conn')
    def test_notify_on_rate_low_rating_regeneration(self, mock_get_conn):
        """Test regeneration trigger for low ratings"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {"avg_rating": 2.0, "cnt": 1}
        mock_get_conn.return_value = mock_conn
        
        rating_payload = {
            "rating": 1,
            "user_id": "user123",
            "comment": "Poor quality"
        }
        
        with patch('core.bhiv_core.save_rating'):
            with patch('core.bhiv_core.bhiv_lm_client.improve_storyboard') as mock_improve:
                # Mock async function to return a coroutine
                async def mock_coro():
                    return {"improvement_applied": True}
                mock_improve.return_value = mock_coro()
                
                with patch('threading.Thread') as mock_thread:
                    result = notify_on_rate(self.test_content_id, rating_payload, regen_threshold=2)
                    
                    assert result["regenerate_triggered"] == True
                    assert result["regenerate_mode"] == "thread"
                    mock_thread.assert_called_once()

    @patch('core.bhiv_core.get_storyboard')
    @patch('core.bhiv_core.get_script')
    def test_regenerate_video_with_storyboard(self, mock_get_script, mock_get_storyboard):
        """Test video regeneration using existing storyboard"""
        mock_storyboard = {
            "scenes": [{"id": "scene_1", "duration": 5.0}],
            "total_duration": 5.0
        }
        mock_get_storyboard.return_value = mock_storyboard
        
        with patch('video.generator.generate_from_storyboard') as mock_generate:
            mock_generate.return_value = {"job_id": "job123", "status": "enqueued"}
            
            result = regenerate_video(self.test_content_id, "low_rating")
            
            assert result["status"] == "enqueued"
            assert result["method"] == "generate_from_storyboard"
            mock_generate.assert_called_once_with(mock_storyboard, content_id=self.test_content_id)

    @patch('core.bhiv_core.get_storyboard')
    @patch('core.bhiv_core.get_script')
    def test_regenerate_video_fallback_to_script(self, mock_get_script, mock_get_storyboard):
        """Test video regeneration fallback to script processing"""
        mock_get_storyboard.return_value = None
        mock_get_script.return_value = self.test_script_content
        
        with patch('core.bhiv_core.process_script_upload') as mock_process:
            mock_process.return_value = {"status": "enqueued", "job_id": "job123"}
            
            with patch('os.makedirs'):
                result = regenerate_video(self.test_content_id, "low_rating")
                
                assert result["status"] == "enqueued"
                assert result["method"] == "process_script_upload"

    @patch('core.bhiv_core.get_storyboard')
    @patch('core.bhiv_core.get_script')
    def test_regenerate_video_no_content(self, mock_get_script, mock_get_storyboard):
        """Test video regeneration with no existing content"""
        mock_get_storyboard.return_value = None
        mock_get_script.return_value = None
        
        result = regenerate_video(self.test_content_id, "low_rating")
        
        assert result["status"] == "failed"
        assert result["reason"] == "no_script_found"

    @patch('core.bhiv_core.get_bucket_path')
    def test_get_content_metadata_from_json(self, mock_get_path):
        """Test content metadata retrieval from JSON file"""
        metadata = {
            "content_id": self.test_content_id,
            "title": "Test Content",
            "processing_status": "completed"
        }
        
        mock_path = f"/bucket/logs/{self.test_content_id}.json"
        mock_get_path.return_value = mock_path
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', mock_open_read_json(metadata)):
                result = get_content_metadata(self.test_content_id)
                
                assert result == metadata
                assert result["content_id"] == self.test_content_id

    def test_get_content_metadata_not_found(self):
        """Test content metadata retrieval when not found"""
        with patch('pathlib.Path.exists', return_value=False):
            result = get_content_metadata("nonexistent")
            assert result is None

    @patch('core.bhiv_core.get_bucket_path')
    def test_log_processing_event(self, mock_get_path):
        """Test processing event logging"""
        mock_path = "/bucket/logs/test_log.log"
        mock_get_path.return_value = mock_path
        
        metadata = {"test": "data"}
        
        with patch('builtins.open', mock_open_write()) as mock_file:
            log_processing_event(self.test_content_id, "test_event", metadata)
            
            # Verify file was opened for append
            mock_file.assert_called_once()
            
            # Verify JSON was written
            written_content = mock_file.return_value.__enter__.return_value.write.call_args[0][0]
            assert self.test_content_id in written_content
            assert "test_event" in written_content

    def test_get_db_conn(self):
        """Test database connection creation"""
        with patch('sqlite3.connect') as mock_connect:
            mock_conn = Mock()
            mock_connect.return_value = mock_conn
            
            conn = _get_db_conn()
            
            mock_connect.assert_called_once()
            mock_conn.execute.assert_called()  # Table creation
            mock_conn.commit.assert_called()
            assert conn == mock_conn

    @pytest.mark.asyncio
    async def test_process_script_upload_error_handling(self):
        """Test error handling in script upload"""
        with patch('core.bhiv_core.save_script', side_effect=Exception("Save failed")):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(self.test_script_content)
                tmp_file.flush()
                
                try:
                    with pytest.raises(ValueError, match="Script processing failed"):
                        await process_script_upload(tmp_file.name, "test_user")
                        
                finally:
                    os.unlink(tmp_file.name)

    def test_notify_on_rate_invalid_rating(self):
        """Test rating notification with invalid rating"""
        rating_payload = {
            "rating": "invalid",
            "user_id": "user123"
        }
        
        with patch('core.bhiv_core._get_db_conn') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {"avg_rating": None, "cnt": 0}
            mock_get_conn.return_value = mock_conn
            
            with patch('core.bhiv_core.save_rating'):
                result = notify_on_rate(self.test_content_id, rating_payload)
                
                assert result["rating"] == 0  # Should default to 0 for invalid rating


def mock_open_read_json(data):
    """Helper to mock file reading with JSON data"""
    import json
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(data))

def mock_open_write():
    """Helper to mock file writing"""
    from unittest.mock import mock_open
    return mock_open()