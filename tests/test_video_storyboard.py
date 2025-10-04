#!/usr/bin/env python3
"""
Unit tests for Video Storyboard Generation
Tests storyboard generation, validation, and text wrapping functionality
"""

import pytest
import json
from unittest.mock import Mock, patch
from video.storyboard import (
    generate_storyboard_from_text, validate_storyboard, wrap_text_for_storyboard,
    save_storyboard_to_file, load_storyboard_from_file, get_storyboard_stats
)

class TestVideoStoryboard:
    
    def test_generate_storyboard_from_text_basic(self):
        """Test basic storyboard generation from text"""
        script_text = "Line 1\nLine 2\nLine 3"
        
        storyboard = generate_storyboard_from_text(script_text)
        
        assert storyboard["version"] == "1.0"
        assert len(storyboard["scenes"]) == 3
        assert storyboard["total_duration"] > 0
        
        # Check first scene
        first_scene = storyboard["scenes"][0]
        assert first_scene["id"] == "scene_1"
        assert first_scene["start_time"] == 0
        assert first_scene["duration"] > 0
        assert len(first_scene["frames"]) == 1
        
        # Check first frame
        first_frame = first_scene["frames"][0]
        assert first_frame["id"] == "frame_1_1"
        assert "Line 1" in first_frame["text"]

    def test_generate_storyboard_empty_text(self):
        """Test error handling for empty script text"""
        with pytest.raises(ValueError, match="Script text cannot be empty"):
            generate_storyboard_from_text("")
        
        with pytest.raises(ValueError, match="Script text cannot be empty"):
            generate_storyboard_from_text("   ")

    def test_generate_storyboard_single_line(self):
        """Test storyboard generation with single line"""
        script_text = "This is a single line of text"
        
        storyboard = generate_storyboard_from_text(script_text)
        
        assert len(storyboard["scenes"]) == 1
        assert storyboard["scenes"][0]["frames"][0]["text"] == script_text

    def test_generate_storyboard_with_empty_lines(self):
        """Test handling of empty lines in script"""
        script_text = "Line 1\n\nLine 2\n   \nLine 3"
        
        storyboard = generate_storyboard_from_text(script_text)
        
        # Should only create scenes for non-empty lines
        assert len(storyboard["scenes"]) == 3
        assert "Line 1" in storyboard["scenes"][0]["frames"][0]["text"]
        assert "Line 2" in storyboard["scenes"][1]["frames"][0]["text"]
        assert "Line 3" in storyboard["scenes"][2]["frames"][0]["text"]

    def test_generate_storyboard_duration_calculation(self):
        """Test duration calculation based on text length"""
        short_text = "Short"
        long_text = "This is a very long line of text that should have a longer duration"
        
        short_storyboard = generate_storyboard_from_text(short_text)
        long_storyboard = generate_storyboard_from_text(long_text)
        
        short_duration = short_storyboard["scenes"][0]["duration"]
        long_duration = long_storyboard["scenes"][0]["duration"]
        
        # Longer text should have longer duration (within limits)
        assert short_duration >= 3.0  # Minimum duration
        assert long_duration <= 6.0   # Maximum duration
        assert long_duration >= short_duration

    def test_generate_storyboard_html_escaping(self):
        """Test HTML escaping in script text"""
        script_text = "<script>alert('test')</script>\n& special chars"
        
        storyboard = generate_storyboard_from_text(script_text)
        
        # Should escape HTML entities
        frame_text = storyboard["scenes"][0]["frames"][0]["text"]
        assert "<script>" not in frame_text
        assert "&lt;script&gt;" in frame_text

    def test_wrap_text_for_storyboard_short_text(self):
        """Test text wrapping for short text"""
        text = "Short text"
        result = wrap_text_for_storyboard(text)
        
        assert result == text
        assert "\n" not in result

    def test_wrap_text_for_storyboard_long_text(self):
        """Test text wrapping for long text"""
        text = "This is a very long line of text that should be wrapped into multiple lines"
        result = wrap_text_for_storyboard(text, max_chars_per_line=30)
        
        lines = result.split("\n")
        assert len(lines) <= 2  # Should wrap to maximum 2 lines
        assert all(len(line) <= 30 for line in lines if line)

    def test_wrap_text_for_storyboard_empty_text(self):
        """Test text wrapping for empty text"""
        assert wrap_text_for_storyboard("") == ""
        assert wrap_text_for_storyboard("   ") == ""

    def test_validate_storyboard_valid(self):
        """Test validation of valid storyboard"""
        valid_storyboard = {
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
                            "text": "Test frame",
                            "text_position": "center"
                        }
                    ]
                }
            ]
        }
        
        assert validate_storyboard(valid_storyboard) == True

    def test_validate_storyboard_invalid_structure(self):
        """Test validation of invalid storyboard structures"""
        # Not a dictionary
        assert validate_storyboard("invalid") == False
        assert validate_storyboard(None) == False
        assert validate_storyboard([]) == False
        
        # Missing scenes
        assert validate_storyboard({}) == False
        assert validate_storyboard({"version": "1.0"}) == False
        
        # Empty scenes
        assert validate_storyboard({"scenes": []}) == False
        
        # Invalid scenes structure
        assert validate_storyboard({"scenes": ["invalid"]}) == False

    def test_validate_storyboard_invalid_scene(self):
        """Test validation of invalid scene structure"""
        invalid_scene_storyboard = {
            "scenes": [
                {
                    "id": "scene_1",
                    # Missing required fields: start_time, duration, frames
                }
            ]
        }
        
        assert validate_storyboard(invalid_scene_storyboard) == False

    def test_validate_storyboard_invalid_frames(self):
        """Test validation of invalid frames structure"""
        invalid_frames_storyboard = {
            "scenes": [
                {
                    "id": "scene_1",
                    "start_time": 0,
                    "duration": 5.0,
                    "frames": []  # Empty frames
                }
            ]
        }
        
        assert validate_storyboard(invalid_frames_storyboard) == False
        
        # Invalid frame structure
        invalid_frame_storyboard = {
            "scenes": [
                {
                    "id": "scene_1",
                    "start_time": 0,
                    "duration": 5.0,
                    "frames": [
                        {
                            "id": "frame_1_1"
                            # Missing required field: text
                        }
                    ]
                }
            ]
        }
        
        assert validate_storyboard(invalid_frame_storyboard) == False

    @patch('core.bhiv_bucket.save_storyboard')
    def test_save_storyboard_to_file(self, mock_save):
        """Test saving storyboard to file"""
        mock_save.return_value = "/path/to/storyboard.json"
        
        storyboard = {"scenes": [{"id": "scene_1"}]}
        result = save_storyboard_to_file(storyboard, "test_storyboard")
        
        mock_save.assert_called_once_with(storyboard, "test_storyboard.json")
        assert result == "/path/to/storyboard.json"

    @patch('core.bhiv_bucket.save_storyboard')
    def test_save_storyboard_to_file_with_extension(self, mock_save):
        """Test saving storyboard with .json extension already present"""
        mock_save.return_value = "/path/to/storyboard.json"
        
        storyboard = {"scenes": [{"id": "scene_1"}]}
        result = save_storyboard_to_file(storyboard, "test_storyboard.json")
        
        mock_save.assert_called_once_with(storyboard, "test_storyboard.json")

    @patch('core.bhiv_bucket.save_storyboard')
    def test_save_storyboard_to_file_error(self, mock_save):
        """Test error handling when saving storyboard fails"""
        mock_save.side_effect = Exception("Save failed")
        
        storyboard = {"scenes": [{"id": "scene_1"}]}
        
        with pytest.raises(ValueError, match="Failed to save storyboard"):
            save_storyboard_to_file(storyboard, "test_storyboard")

    @patch('core.bhiv_bucket.read_storyboard')
    def test_load_storyboard_from_file(self, mock_read):
        """Test loading storyboard from file"""
        valid_storyboard = {
            "scenes": [
                {
                    "id": "scene_1",
                    "start_time": 0,
                    "duration": 5.0,
                    "frames": [{"id": "frame_1_1", "text": "Test"}]
                }
            ]
        }
        mock_read.return_value = valid_storyboard
        
        result = load_storyboard_from_file("test_storyboard.json")
        
        mock_read.assert_called_once_with("test_storyboard.json")
        assert result == valid_storyboard

    @patch('core.bhiv_bucket.read_storyboard')
    def test_load_storyboard_from_file_invalid(self, mock_read):
        """Test loading invalid storyboard from file"""
        invalid_storyboard = {"invalid": "structure"}
        mock_read.return_value = invalid_storyboard
        
        with pytest.raises(ValueError, match="Invalid storyboard format"):
            load_storyboard_from_file("test_storyboard.json")

    @patch('core.bhiv_bucket.read_storyboard')
    def test_load_storyboard_from_file_error(self, mock_read):
        """Test error handling when loading storyboard fails"""
        mock_read.side_effect = Exception("Read failed")
        
        with pytest.raises(ValueError, match="Failed to load storyboard"):
            load_storyboard_from_file("test_storyboard.json")

    def test_get_storyboard_stats(self):
        """Test getting storyboard statistics"""
        storyboard = {
            "version": "1.0",
            "total_duration": 15.5,
            "scenes": [
                {
                    "id": "scene_1",
                    "start_time": 0,
                    "duration": 5.0,
                    "frames": [
                        {"id": "frame_1_1", "text": "Frame 1"},
                        {"id": "frame_1_2", "text": "Frame 2"}
                    ]
                },
                {
                    "id": "scene_2",
                    "start_time": 5.0,
                    "duration": 10.5,
                    "frames": [
                        {"id": "frame_2_1", "text": "Frame 3"}
                    ]
                }
            ]
        }
        
        stats = get_storyboard_stats(storyboard)
        
        assert stats["total_scenes"] == 2
        assert stats["total_frames"] == 3
        assert stats["total_duration"] == 15.5
        assert stats["avg_scene_duration"] == 7.75  # (5.0 + 10.5) / 2

    def test_get_storyboard_stats_invalid(self):
        """Test getting stats for invalid storyboard"""
        invalid_storyboard = {"invalid": "structure"}
        
        with pytest.raises(ValueError, match="Invalid storyboard"):
            get_storyboard_stats(invalid_storyboard)

    def test_get_storyboard_stats_empty_scenes(self):
        """Test getting stats for storyboard with no scenes"""
        empty_storyboard = {"scenes": []}
        
        with pytest.raises(ValueError, match="Invalid storyboard"):
            get_storyboard_stats(empty_storyboard)

    @patch('video.failed_cases.archive_failed_storyboard')
    def test_generate_storyboard_error_archiving(self, mock_archive):
        """Test error archiving when storyboard generation fails"""
        script_text = "Test script"
        
        # Mock HTML escaping to raise an exception
        with patch('html.escape', side_effect=Exception("HTML escape failed")):
            with pytest.raises(Exception, match="HTML escape failed"):
                generate_storyboard_from_text(script_text)
            
            # Should archive the failed case
            mock_archive.assert_called_once()
            args = mock_archive.call_args[0]
            assert args[0] == script_text
            assert "HTML escape failed" in args[1]
            assert args[2] == "storyboard_generation"

    def test_wrap_text_for_storyboard_exact_limit(self):
        """Test text wrapping at exact character limit"""
        text = "A" * 50  # Exactly 50 characters
        result = wrap_text_for_storyboard(text, max_chars_per_line=50)
        
        assert result == text
        assert "\n" not in result

    def test_wrap_text_for_storyboard_word_boundary(self):
        """Test text wrapping respects word boundaries"""
        text = "This is a test of word boundary wrapping functionality"
        result = wrap_text_for_storyboard(text, max_chars_per_line=20)
        
        lines = result.split("\n")
        # Should not break words in the middle
        for line in lines:
            if line.strip():
                assert not line.endswith(" ")
                assert not line.startswith(" ")

    def test_generate_storyboard_timing_sequence(self):
        """Test that scene timing is sequential"""
        script_text = "Scene 1\nScene 2\nScene 3"
        
        storyboard = generate_storyboard_from_text(script_text)
        
        scenes = storyboard["scenes"]
        assert scenes[0]["start_time"] == 0
        assert scenes[1]["start_time"] == 4.0  # time_per_scene
        assert scenes[2]["start_time"] == 8.0  # 2 * time_per_scene
        
        # Total duration should match sum of scene durations
        expected_total = sum(scene["duration"] for scene in scenes)
        assert storyboard["total_duration"] == expected_total