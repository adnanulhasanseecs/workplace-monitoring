"""
Unit tests for video ingestion validator.
"""
import sys
from pathlib import Path
import pytest
from tempfile import NamedTemporaryFile

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from ingestion.validator import VideoValidator


def test_validate_rtsp_url():
    """Test RTSP URL validation."""
    validator = VideoValidator()
    
    # Valid RTSP URL
    is_valid, error = validator.validate_stream_url("rtsp://example.com/stream", "rtsp")
    assert is_valid is True
    assert error is None
    
    # Invalid RTSP URL
    is_valid, error = validator.validate_stream_url("http://example.com/stream", "rtsp")
    assert is_valid is False
    assert "RTSP" in error


def test_validate_http_url():
    """Test HTTP URL validation."""
    validator = VideoValidator()
    
    # Valid HTTP URL
    is_valid, error = validator.validate_stream_url("http://example.com/stream", "http")
    assert is_valid is True
    
    # Valid HTTPS URL
    is_valid, error = validator.validate_stream_url("https://example.com/stream", "http")
    assert is_valid is True
    
    # Invalid HTTP URL
    is_valid, error = validator.validate_stream_url("rtsp://example.com/stream", "http")
    assert is_valid is False


def test_validate_file_path():
    """Test file path validation."""
    validator = VideoValidator()
    
    # Create a temporary file
    with NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    
    try:
        # Valid file
        is_valid, error = validator.validate_stream_url(str(tmp_path), "file")
        assert is_valid is True
        
        # Invalid file (doesn't exist)
        is_valid, error = validator.validate_stream_url("/nonexistent/file.mp4", "file")
        assert is_valid is False
        
        # Invalid extension
        with NamedTemporaryFile(suffix=".txt", delete=False) as tmp2:
            txt_path = Path(tmp2.name)
        try:
            is_valid, error = validator.validate_stream_url(str(txt_path), "file")
            assert is_valid is False
            assert "Unsupported" in error
        finally:
            txt_path.unlink()
    finally:
        tmp_path.unlink()


def test_validate_file_upload():
    """Test file upload validation."""
    validator = VideoValidator()
    
    # Create a temporary file
    with NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(b"test video content")
        tmp_path = Path(tmp.name)
    
    try:
        # Valid file
        is_valid, error = validator.validate_file_upload(tmp_path)
        assert is_valid is True
        
        # Empty file
        empty_path = tmp_path.parent / "empty.mp4"
        empty_path.touch()
        try:
            is_valid, error = validator.validate_file_upload(empty_path)
            assert is_valid is False
            assert "empty" in error.lower()
        finally:
            empty_path.unlink()
    finally:
        tmp_path.unlink()

