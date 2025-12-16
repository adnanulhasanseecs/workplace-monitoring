"""
HTTP stream handler.
"""
import cv2
from typing import Optional
import requests
from pathlib import Path

from observability.logging import get_logger

logger = get_logger(__name__)


class HTTPHandler:
    """Handler for HTTP/HTTPS video streams."""
    
    def __init__(self, stream_url: str, timeout: int = 10):
        """
        Initialize HTTP handler.
        
        Args:
            stream_url: HTTP/HTTPS stream URL
            timeout: Connection timeout in seconds
        """
        self.stream_url = stream_url
        self.timeout = timeout
        self.cap: Optional[cv2.VideoCapture] = None
    
    def connect(self) -> bool:
        """
        Connect to HTTP stream.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Test URL accessibility
            response = requests.head(self.stream_url, timeout=self.timeout, allow_redirects=True)
            if response.status_code not in [200, 301, 302]:
                logger.error(f"HTTP stream returned status {response.status_code}: {self.stream_url}")
                return False
            
            self.cap = cv2.VideoCapture(self.stream_url)
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open HTTP stream: {self.stream_url}")
                return False
            
            # Test read
            ret, frame = self.cap.read()
            if not ret:
                logger.error(f"Failed to read from HTTP stream: {self.stream_url}")
                self.cap.release()
                self.cap = None
                return False
            
            logger.info(f"Connected to HTTP stream: {self.stream_url}")
            return True
        
        except requests.RequestException as e:
            logger.error(f"Error connecting to HTTP stream: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to HTTP stream: {e}")
            if self.cap:
                self.cap.release()
                self.cap = None
            return False
    
    def read_frame(self) -> Optional[tuple[bool, any]]:
        """
        Read a single frame from stream.
        
        Returns:
            Tuple of (success, frame) or None if error
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        try:
            ret, frame = self.cap.read()
            return (ret, frame) if ret else None
        except Exception as e:
            logger.error(f"Error reading frame from HTTP stream: {e}")
            return None
    
    def get_stream_info(self) -> Optional[dict]:
        """
        Get stream information.
        
        Returns:
            Dictionary with stream properties or None if unavailable
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        try:
            return {
                "fps": self.cap.get(cv2.CAP_PROP_FPS),
                "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "frame_count": int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            }
        except Exception as e:
            logger.error(f"Error getting stream info: {e}")
            return None
    
    def disconnect(self):
        """Disconnect from stream."""
        if self.cap:
            self.cap.release()
            self.cap = None
            logger.info(f"Disconnected from HTTP stream: {self.stream_url}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

