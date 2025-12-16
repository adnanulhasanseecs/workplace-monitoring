"""
Video input validation utilities.
"""
from typing import Optional
from pathlib import Path
import re

from observability.logging import get_logger

logger = get_logger(__name__)


class VideoValidator:
    """Validator for video inputs (streams and files)."""
    
    # Supported video file extensions
    SUPPORTED_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v'}
    
    # RTSP URL pattern
    RTSP_PATTERN = re.compile(r'^rtsp://', re.IGNORECASE)
    
    # HTTP URL pattern
    HTTP_PATTERN = re.compile(r'^https?://', re.IGNORECASE)
    
    @classmethod
    def validate_stream_url(cls, url: str, stream_type: str) -> tuple[bool, Optional[str]]:
        """
        Validate stream URL format.
        
        Args:
            url: Stream URL
            stream_type: Type of stream (rtsp, http, file)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "Stream URL is required"
        
        if stream_type == "rtsp":
            if not cls.RTSP_PATTERN.match(url):
                return False, "Invalid RTSP URL format. Must start with 'rtsp://'"
        
        elif stream_type == "http":
            if not cls.HTTP_PATTERN.match(url):
                return False, "Invalid HTTP URL format. Must start with 'http://' or 'https://'"
        
        elif stream_type == "file":
            path = Path(url)
            if not path.exists():
                return False, f"File not found: {url}"
            if not path.is_file():
                return False, f"Path is not a file: {url}"
            if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
                return False, f"Unsupported file format. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        else:
            return False, f"Unsupported stream type: {stream_type}"
        
        return True, None
    
    @classmethod
    def validate_file_upload(cls, file_path: Path) -> tuple[bool, Optional[str]]:
        """
        Validate uploaded video file.
        
        Args:
            file_path: Path to uploaded file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not file_path.exists():
            return False, f"File not found: {file_path}"
        
        if not file_path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        if file_path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file format. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        # Check file size (max 10GB)
        max_size = 10 * 1024 * 1024 * 1024  # 10GB
        file_size = file_path.stat().st_size
        if file_size > max_size:
            return False, f"File too large. Maximum size: 10GB, got: {file_size / (1024**3):.2f}GB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None

