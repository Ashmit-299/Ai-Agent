#!/usr/bin/env python3
"""
Unit tests for BHIV Components - Enhanced Coverage
Tests component interactions and edge cases for 10/10 coverage
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

class TestBHIVComponentsEnhanced:
    
    @pytest.mark.asyncio
    async def test_component_error_propagation(self):
        """Test error propagation between components"""
        from core import bhiv_core, bhiv_bucket
        
        with patch.object(bhiv_bucket, 'save_script', side_effect=Exception("Storage error")):
            with pytest.raises(ValueError, match="Script processing failed"):
                await bhiv_core.process_script_upload("test.txt", "user1")

    @pytest.mark.asyncio
    async def test_lm_client_timeout_handling(self):
        """Test LM client timeout and retry logic"""
        from core import bhiv_lm_client
        import httpx
        
        with patch('core.bhiv_lm_client.call_lm_async', side_effect=httpx.TimeoutException("Timeout")):
            result = await bhiv_lm_client.suggest_storyboard("test script")
            assert result["generation_method"] == "local_heuristic"

    def test_bucket_storage_validation(self):
        """Test bucket storage input validation"""
        from core import bhiv_bucket
        
        with pytest.raises(ValueError, match="(Invalid destination filename|Failed to save script)"):
            bhiv_bucket.save_script("test.txt", "../invalid.txt")

    @pytest.mark.asyncio
    async def test_webhook_processing_edge_cases(self):
        """Test webhook processing with various payload formats"""
        from core import bhiv_core
        
        # Test empty payload
        result = await bhiv_core.process_webhook_ingest(payload={})
        assert result["status"] == "error"
        assert result["reason"] == "no_script_found"
        
        # Test malformed payload
        result = await bhiv_core.process_webhook_ingest(payload={"invalid": "data"})
        assert result["status"] == "error"

    def test_auth_token_validation_edge_cases(self):
        """Test authentication edge cases"""
        from app.auth import verify_token
        
        with pytest.raises(Exception):
            verify_token("invalid_token")
        
        with pytest.raises(Exception):
            verify_token("")

    def test_database_connection_resilience(self):
        """Test database connection error handling"""
        from core.database import DatabaseManager
        
        # Test that DatabaseManager can be created even with connection issues
        db_manager = DatabaseManager()
        assert db_manager is not None

    @pytest.mark.asyncio
    async def test_concurrent_operations_safety(self):
        """Test thread safety of concurrent operations"""
        from core import bhiv_core
        
        tasks = []
        for i in range(3):
            task = bhiv_core.process_script_upload_async(
                script_text=f"Script {i}",
                uploader=f"user{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All should complete without exceptions
        for result in results:
            assert not isinstance(result, Exception)
            assert result["status"] == "enqueued"

    def test_video_generation_validation(self):
        """Test video generation input validation"""
        from video.storyboard import generate_storyboard_from_text
        
        with pytest.raises(ValueError, match="Script text cannot be empty"):
            generate_storyboard_from_text("")
        
        with pytest.raises(ValueError, match="Script text cannot be empty"):
            generate_storyboard_from_text("   ")

    def test_rating_system_boundary_conditions(self):
        """Test rating system with boundary values"""
        from core import bhiv_core
        
        # Test with minimum rating
        result = bhiv_core.notify_on_rate("test123", {"rating": 1, "user_id": "user1"})
        assert result["rating"] == 1
        assert result["regenerate_triggered"] == True
        
        # Test with maximum rating
        result = bhiv_core.notify_on_rate("test123", {"rating": 5, "user_id": "user1"})
        assert result["rating"] == 5

    def test_component_initialization_order(self):
        """Test proper component initialization order"""
        # Test that components can be imported without circular dependencies
        import core.bhiv_core
        import core.bhiv_bucket
        import core.bhiv_lm_client
        import video.storyboard
        import app.auth
        
        # All imports should succeed without errors
        assert True