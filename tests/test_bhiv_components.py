#!/usr/bin/env python3
"""
Unit tests for BHIV Components Integration
Tests component compatibility, interaction tests, and integration workflows
"""

import pytest
import asyncio
import tempfile
import json
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

class TestBHIVComponents:
    
    def setup_method(self):
        """Setup test environment"""
        self.test_content_id = "test123"
        self.test_script = "This is a test script for integration testing"
        
    @pytest.mark.asyncio
    async def test_core_bucket_integration(self):
        """Test integration between core and bucket components"""
        from core import bhiv_core, bhiv_bucket
        
        with patch.object(bhiv_bucket, 'save_script') as mock_save_script:
            with patch.object(bhiv_bucket, 'save_storyboard') as mock_save_storyboard:
                with patch.object(bhiv_bucket, 'save_json') as mock_save_json:
                    
                    mock_save_script.return_value = "/bucket/scripts/test.txt"
                    mock_save_storyboard.return_value = "/bucket/storyboards/test.json"
                    mock_save_json.return_value = "/bucket/logs/test.json"
                    
                    # Test that core can successfully interact with bucket
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                        tmp_file.write(self.test_script)
                        tmp_file.flush()
                        
                        try:
                            with patch('video.storyboard.generate_storyboard_from_text') as mock_storyboard:
                                mock_storyboard.return_value = {
                                    "scenes": [{"id": "scene_1", "duration": 5.0}],
                                    "total_duration": 5.0
                                }
                                
                                with patch('video.generator.render_video_from_storyboard') as mock_render:
                                    mock_render.return_value = "/bucket/videos/test.mp4"
                                    
                                    result = await bhiv_core.process_script_upload(
                                        tmp_file.name, "test_user", "Test Integration"
                                    )
                                    
                                    # Verify all bucket operations were called
                                    mock_save_script.assert_called_once()
                                    mock_save_storyboard.assert_called_once()
                                    mock_save_json.assert_called_once()
                                    
                                    assert result["processing_status"] == "completed"
                                    
                        finally:
                            import os
                            os.unlink(tmp_file.name)

    @pytest.mark.asyncio
    async def test_core_lm_client_integration(self):
        """Test integration between core and LM client components"""
        from core import bhiv_core, bhiv_lm_client
        
        mock_storyboard = {
            "scenes": [{"id": "scene_1", "text": "LLM generated scene", "duration": 5.0}],
            "total_duration": 5.0,
            "version": "1.0",
            "llm_enhanced": True
        }
        
        with patch.object(bhiv_lm_client, 'suggest_storyboard') as mock_suggest:
            with patch.object(bhiv_lm_client, 'improve_storyboard') as mock_improve:
                
                mock_suggest.return_value = mock_storyboard
                mock_improve.return_value = {
                    "improvement_applied": True,
                    "changes": ["Adjusted timing"],
                    **mock_storyboard
                }
                
                # Test storyboard suggestion integration
                result = await bhiv_lm_client.suggest_storyboard(self.test_script)
                assert result["llm_enhanced"] == True
                assert len(result["scenes"]) == 1
                
                # Test storyboard improvement integration
                feedback = {"rating": 2, "comment": "Too fast"}
                improved = await bhiv_lm_client.improve_storyboard(mock_storyboard, feedback)
                assert improved["improvement_applied"] == True

    def test_bucket_video_integration(self):
        """Test integration between bucket and video components"""
        from core import bhiv_bucket
        from video import storyboard
        
        # Test storyboard generation and saving
        test_storyboard = storyboard.generate_storyboard_from_text(self.test_script)
        
        with patch.object(bhiv_bucket, 'save_storyboard') as mock_save:
            mock_save.return_value = "/bucket/storyboards/test.json"
            
            result = storyboard.save_storyboard_to_file(test_storyboard, "test_storyboard")
            
            mock_save.assert_called_once_with(test_storyboard, "test_storyboard.json")
            assert result == "/bucket/storyboards/test.json"

    @pytest.mark.asyncio
    async def test_webhook_to_video_pipeline(self):
        """Test complete webhook to video generation pipeline"""
        from core import bhiv_core
        
        webhook_payload = {
            "script": "Webhook generated script content",
            "source": "external_api",
            "metadata": {"type": "automated"}
        }
        
        with patch('core.bhiv_core.save_json') as mock_save_json:
            with patch('core.bhiv_core.save_text') as mock_save_text:
                with patch('core.bhiv_core.process_script_upload') as mock_process:
                    
                    mock_process.return_value = {
                        "status": "completed",
                        "content_id": "webhook123",
                        "processing_status": "completed"
                    }
                    
                    result = await bhiv_core.process_webhook_ingest(payload=webhook_payload)
                    
                    assert result["status"] == "ok"
                    assert "content_id" in result
                    assert result["note"] == "pipeline_invoked"
                    
                    # Verify pipeline was triggered
                    mock_process.assert_called_once()

    def test_rating_feedback_loop_integration(self):
        """Test rating and feedback loop integration"""
        from core import bhiv_core
        
        rating_payload = {
            "rating": 1,
            "user_id": "user123",
            "comment": "Poor quality, needs improvement"
        }
        
        with patch('core.bhiv_core._get_db_conn') as mock_get_conn:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = {"avg_rating": 1.5, "cnt": 2}
            mock_get_conn.return_value = mock_conn
            
            with patch('core.bhiv_core.save_rating') as mock_save_rating:
                with patch('core.bhiv_core.get_storyboard') as mock_get_storyboard:
                    with patch('core.bhiv_core.bhiv_lm_client.improve_storyboard') as mock_improve:
                        
                        mock_get_storyboard.return_value = {
                            "scenes": [{"id": "scene_1", "duration": 5.0}]
                        }
                        
                        # Mock async improvement
                        future = asyncio.Future()
                        future.set_result({"improvement_applied": True})
                        mock_improve.return_value = future
                        
                        with patch('threading.Thread') as mock_thread:
                            result = bhiv_core.notify_on_rate(self.test_content_id, rating_payload)
                            
                            # Verify complete feedback loop
                            assert result["status"] == "ok"
                            assert result["regenerate_triggered"] == True
                            assert "storyboard_improvement" in result
                            
                            mock_save_rating.assert_called_once()
                            mock_thread.assert_called_once()

    def test_auth_database_integration(self):
        """Test authentication and database integration"""
        from app import auth
        from core.database import DatabaseManager
        
        with patch.object(DatabaseManager, 'get_user_by_username') as mock_get_user:
            with patch.object(DatabaseManager, 'create_user') as mock_create_user:
                
                # Test user registration flow
                mock_get_user.return_value = None  # User doesn't exist
                mock_create_user.return_value = Mock(
                    user_id="user123",
                    username="testuser",
                    email="test@example.com"
                )
                
                # Verify auth can interact with database
                user_data = {
                    "user_id": "user123",
                    "username": "testuser",
                    "password_hash": auth.hash_password("password123"),
                    "email": "test@example.com"
                }
                
                # Test password hashing integration
                hashed = auth.hash_password("password123")
                assert auth.verify_password("password123", hashed) == True
                assert auth.verify_password("wrongpassword", hashed) == False

    @pytest.mark.asyncio
    async def test_error_propagation_across_components(self):
        """Test error handling and propagation across components"""
        from core import bhiv_core, bhiv_bucket
        
        # Test error propagation from bucket to core
        with patch.object(bhiv_bucket, 'save_script', side_effect=Exception("Bucket error")):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp_file:
                tmp_file.write(self.test_script)
                tmp_file.flush()
                
                try:
                    with pytest.raises(ValueError, match="Script processing failed"):
                        await bhiv_core.process_script_upload(tmp_file.name, "test_user")
                        
                finally:
                    import os
                    os.unlink(tmp_file.name)

    def test_video_storyboard_validation_integration(self):
        """Test video and storyboard validation integration"""
        from video import storyboard
        
        # Test valid storyboard generation and validation
        valid_script = "Scene 1: Introduction\nScene 2: Main content\nScene 3: Conclusion"
        generated_storyboard = storyboard.generate_storyboard_from_text(valid_script)
        
        # Verify generated storyboard passes validation
        assert storyboard.validate_storyboard(generated_storyboard) == True
        
        # Test storyboard statistics
        stats = storyboard.get_storyboard_stats(generated_storyboard)
        assert stats["total_scenes"] == 3
        assert stats["total_duration"] > 0

    def test_lm_client_fallback_integration(self):
        """Test LM client fallback integration with video components"""
        from core import bhiv_lm_client
        from video import storyboard
        
        # Test fallback when LLM is unavailable
        with patch('core.bhiv_lm_client.BHIV_LM_URL', ''):
            with patch.object(storyboard, 'generate_storyboard_from_text') as mock_generate:
                mock_generate.return_value = {
                    "scenes": [{"id": "scene_1", "duration": 5.0}],
                    "total_duration": 5.0,
                    "version": "1.0"
                }
                
                async def test_fallback():
                    result = await bhiv_lm_client.suggest_storyboard(self.test_script)
                    assert result["generation_method"] == "local_heuristic"
                    assert result["llm_enhanced"] == False
                    mock_generate.assert_called_once()
                
                asyncio.run(test_fallback())

    def test_bucket_storage_backend_compatibility(self):
        """Test bucket storage backend compatibility"""
        from core import bhiv_bucket
        
        # Test local storage backend
        with patch('core.bhiv_bucket.STORAGE_BACKEND', 'local'):
            with patch('core.bhiv_bucket.init_bucket'):
                with patch('shutil.copy') as mock_copy:
                    with tempfile.NamedTemporaryFile() as tmp_file:
                        result = bhiv_bucket.save_script(tmp_file.name, "test.txt")
                        mock_copy.assert_called_once()
                        assert "test.txt" in result

        # Test S3 storage backend
        with patch('core.bhiv_bucket.STORAGE_BACKEND', 's3'):
            with patch('core.bhiv_bucket._get_s3_client') as mock_get_client:
                mock_s3_client = Mock()
                mock_get_client.return_value = mock_s3_client
                
                with tempfile.NamedTemporaryFile() as tmp_file:
                    result = bhiv_bucket.save_script(tmp_file.name, "test.txt")
                    mock_s3_client.upload_file.assert_called_once()
                    assert result.startswith("s3://")

    @pytest.mark.asyncio
    async def test_concurrent_operations_integration(self):
        """Test concurrent operations across components"""
        from core import bhiv_core
        
        # Test multiple concurrent script uploads
        tasks = []
        for i in range(3):
            task = bhiv_core.process_script_upload_async(
                script_text=f"Script {i} content",
                uploader=f"user{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        # All should be enqueued successfully
        for result in results:
            assert result["status"] == "enqueued"
            assert "job_id" in result

    def test_configuration_integration(self):
        """Test configuration integration across components"""
        from core import bhiv_lm_client, bhiv_bucket
        
        # Test LM client configuration
        config = bhiv_lm_client.get_llm_config()
        assert "llm_url_configured" in config
        assert "api_key_configured" in config
        assert "fallback_enabled" in config
        
        # Test bucket storage configuration
        stats = bhiv_bucket.get_storage_stats()
        assert "backend" in stats
        assert "segments" in stats
        assert len(stats["segments"]) == 7

    def test_data_flow_integration(self):
        """Test data flow between components"""
        from core import bhiv_bucket
        
        # Test data persistence and retrieval
        test_data = {
            "content_id": self.test_content_id,
            "title": "Test Content",
            "status": "completed"
        }
        
        with patch.object(bhiv_bucket, 'save_json') as mock_save:
            with patch.object(bhiv_bucket, 'get_bucket_path') as mock_get_path:
                
                mock_save.return_value = "/bucket/logs/test.json"
                mock_get_path.return_value = "/bucket/logs/test.json"
                
                # Save data
                result = bhiv_bucket.save_json("logs", "test.json", test_data)
                assert result == "/bucket/logs/test.json"
                
                # Verify save was called with correct data
                mock_save.assert_called_once_with("logs", "test.json", test_data)

    def test_component_isolation_and_mocking(self):
        """Test that components can be properly isolated and mocked"""
        from core import bhiv_core
        
        # Test that components can be mocked independently
        with patch('core.bhiv_bucket.save_script') as mock_bucket:
            with patch('video.storyboard.generate_storyboard_from_text') as mock_video:
                with patch('core.bhiv_lm_client.suggest_storyboard') as mock_lm:
                    
                    mock_bucket.return_value = "/bucket/scripts/test.txt"
                    mock_video.return_value = {"scenes": [], "total_duration": 0}
                    mock_lm.side_effect = Exception("LLM unavailable")
                    
                    # Each component should be independently mockable
                    assert mock_bucket.return_value == "/bucket/scripts/test.txt"
                    assert mock_video.return_value["scenes"] == []
                    
                    # LM client should be able to fail independently
                    with pytest.raises(Exception, match="LLM unavailable"):
                        raise mock_lm.side_effect

    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow integration"""
        from core import bhiv_core
        
        # Simulate complete workflow: webhook -> processing -> rating -> improvement
        webhook_payload = {"script": "End-to-end test script"}
        
        with patch('core.bhiv_core.save_json'):
            with patch('core.bhiv_core.save_text'):
                with patch('core.bhiv_core.process_script_upload') as mock_process:
                    
                    mock_process.return_value = {
                        "content_id": "e2e123",
                        "processing_status": "completed"
                    }
                    
                    # Step 1: Webhook ingestion
                    webhook_result = await bhiv_core.process_webhook_ingest(payload=webhook_payload)
                    assert webhook_result["status"] == "ok"
                    
                    # Step 2: Rating and feedback
                    rating_payload = {"rating": 2, "comment": "Needs improvement"}
                    
                    with patch('core.bhiv_core._get_db_conn') as mock_conn:
                        mock_conn.return_value.cursor.return_value.fetchone.return_value = {
                            "avg_rating": 2.0, "cnt": 1
                        }
                        
                        with patch('core.bhiv_core.save_rating'):
                            with patch('core.bhiv_core.bhiv_lm_client.improve_storyboard') as mock_improve:
                                future = asyncio.Future()
                                future.set_result({"improvement_applied": True})
                                mock_improve.return_value = future
                                
                                rating_result = bhiv_core.notify_on_rate("e2e123", rating_payload)
                                assert rating_result["status"] == "ok"
                                assert "storyboard_improvement" in rating_result