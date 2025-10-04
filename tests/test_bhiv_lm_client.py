#!/usr/bin/env python3
"""
Unit tests for BHIV LM Client
Tests LLM integration, fallback mechanisms, retry logic, and timeout handling
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import httpx
from core.bhiv_lm_client import (
    suggest_storyboard, improve_storyboard, call_lm_async,
    _fallback_suggest_storyboard, _fallback_improve_storyboard,
    LMError, is_llm_configured, get_llm_config
)

class TestBHIVLMClient:
    
    @pytest.mark.asyncio
    async def test_suggest_storyboard_success(self):
        """Test successful storyboard suggestion"""
        mock_response = {
            "scenes": [{"id": "scene_1", "text": "Test scene", "duration": 5.0}],
            "total_duration": 5.0,
            "version": "1.0"
        }
        
        with patch('core.bhiv_lm_client.call_lm_async', return_value=mock_response):
            result = await suggest_storyboard("Test script")
            
            assert result == mock_response
            assert "scenes" in result
            assert len(result["scenes"]) == 1

    @pytest.mark.asyncio
    async def test_suggest_storyboard_fallback_on_timeout(self):
        """Test fallback when LLM times out"""
        with patch('core.bhiv_lm_client.call_lm_async', side_effect=httpx.TimeoutException("Timeout")):
            with patch('core.bhiv_lm_client._fallback_suggest_storyboard') as mock_fallback:
                mock_fallback.return_value = {"fallback": True}
                
                result = await suggest_storyboard("Test script")
                
                mock_fallback.assert_called_once_with("Test script")
                assert result == {"fallback": True}

    @pytest.mark.asyncio
    async def test_suggest_storyboard_fallback_on_error(self):
        """Test fallback when LLM returns error"""
        with patch('core.bhiv_lm_client.call_lm_async', side_effect=LMError("API Error")):
            with patch('core.bhiv_lm_client._fallback_suggest_storyboard') as mock_fallback:
                mock_fallback.return_value = {"fallback": True}
                
                result = await suggest_storyboard("Test script")
                
                mock_fallback.assert_called_once_with("Test script")

    @pytest.mark.asyncio
    async def test_improve_storyboard_success(self):
        """Test successful storyboard improvement"""
        storyboard = {"scenes": [{"id": "scene_1", "duration": 5.0}]}
        feedback = {"rating": 2, "comment": "Too fast"}
        mock_response = {"improved": True, "scenes": [{"id": "scene_1", "duration": 7.0}]}
        
        with patch('core.bhiv_lm_client.call_lm_async', return_value=mock_response):
            result = await improve_storyboard(storyboard, feedback)
            
            assert result == mock_response
            assert result["improved"] == True

    @pytest.mark.asyncio
    async def test_improve_storyboard_fallback(self):
        """Test fallback improvement logic"""
        storyboard = {"scenes": [{"id": "scene_1", "duration": 5.0}]}
        feedback = {"rating": 2, "comment": "Too fast"}
        
        with patch('core.bhiv_lm_client.call_lm_async', side_effect=LMError("API Error")):
            result = await improve_storyboard(storyboard, feedback)
            
            assert "generation_method" in result
            assert result["generation_method"] == "local_heuristic_improved"
            assert result["improvement_applied"] == True

    @pytest.mark.asyncio
    async def test_call_lm_async_success(self):
        """Test successful LM API call"""
        mock_response = {"result": "success"}
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response_obj)
            
            result = await call_lm_async("test prompt")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_call_lm_async_rate_limit(self):
        """Test rate limit handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 429
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response_obj)
            
            with pytest.raises(LMError, match="rate_limited"):
                await call_lm_async("test prompt")

    @pytest.mark.asyncio
    async def test_call_lm_async_server_error(self):
        """Test server error handling"""
        with patch('httpx.AsyncClient') as mock_client:
            mock_response_obj = Mock()
            mock_response_obj.status_code = 500
            
            mock_client.return_value.__aenter__.return_value.post = AsyncMock(return_value=mock_response_obj)
            
            with pytest.raises(LMError, match="server_error"):
                await call_lm_async("test prompt")

    @pytest.mark.asyncio
    async def test_fallback_suggest_storyboard(self):
        """Test local fallback storyboard generation"""
        script_text = "This is a test script for storyboard generation"
        
        with patch('video.storyboard.generate_storyboard_from_text') as mock_generate:
            mock_storyboard = {
                "scenes": [{"id": "scene_1", "text": "Test", "duration": 5.0}],
                "total_duration": 5.0,
                "version": "1.0"
            }
            mock_generate.return_value = mock_storyboard
            
            result = await _fallback_suggest_storyboard(script_text)
            
            assert result["generation_method"] == "local_heuristic"
            assert result["llm_enhanced"] == False
            assert "scenes" in result

    @pytest.mark.asyncio
    async def test_fallback_suggest_storyboard_minimal(self):
        """Test minimal fallback when local generation fails"""
        script_text = "Test script"
        
        with patch('video.storyboard.generate_storyboard_from_text', side_effect=Exception("Error")):
            result = await _fallback_suggest_storyboard(script_text)
            
            assert result["generation_method"] == "minimal_fallback"
            assert result["llm_enhanced"] == False
            assert len(result["scenes"]) == 1
            assert result["scenes"][0]["frames"][0]["text"] == script_text

    @pytest.mark.asyncio
    async def test_fallback_improve_storyboard_low_rating(self):
        """Test improvement for low rating"""
        storyboard = {
            "scenes": [{"id": "scene_1", "duration": 5.0}],
            "total_duration": 5.0
        }
        feedback = {"rating": 2, "comment": "Too fast"}
        
        result = await _fallback_improve_storyboard(storyboard, feedback)
        
        assert result["improvement_applied"] == True
        assert result["scenes"][0]["duration"] == 6.0  # 5.0 * 1.2
        assert result["total_duration"] == 6.0

    @pytest.mark.asyncio
    async def test_fallback_improve_storyboard_high_rating(self):
        """Test improvement for high rating"""
        storyboard = {
            "scenes": [{"id": "scene_1", "duration": 5.0}],
            "total_duration": 5.0
        }
        feedback = {"rating": 5, "comment": "Great but too slow"}
        
        result = await _fallback_improve_storyboard(storyboard, feedback)
        
        assert result["improvement_applied"] == True
        assert result["scenes"][0]["duration"] == 4.5  # 5.0 * 0.9
        assert result["total_duration"] == 4.5

    def test_is_llm_configured(self):
        """Test LLM configuration check"""
        with patch.dict('os.environ', {'BHIV_LM_URL': 'http://test', 'BHIV_LM_API_KEY': 'test_key'}):
            assert is_llm_configured() == True
        
        with patch.dict('os.environ', {}, clear=True):
            assert is_llm_configured() == False

    def test_get_llm_config(self):
        """Test LLM configuration retrieval"""
        with patch.dict('os.environ', {'BHIV_LM_URL': 'http://test', 'BHIV_LM_API_KEY': 'test_key'}):
            config = get_llm_config()
            
            assert config["llm_url_configured"] == True
            assert config["api_key_configured"] == True
            assert config["fallback_enabled"] == True
            assert "timeout_seconds" in config

    @pytest.mark.asyncio
    async def test_suggest_storyboard_empty_script(self):
        """Test handling of empty script"""
        with patch('core.bhiv_lm_client._fallback_suggest_storyboard') as mock_fallback:
            mock_fallback.return_value = {"minimal": True}
            
            result = await suggest_storyboard("")
            mock_fallback.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_improve_storyboard_error_handling(self):
        """Test error handling in improvement"""
        storyboard = {"invalid": "storyboard"}
        feedback = {"rating": 3}
        
        result = await _fallback_improve_storyboard(storyboard, feedback)
        
        # Should return original storyboard with error
        assert "improvement_error" in result
        assert result["invalid"] == "storyboard"