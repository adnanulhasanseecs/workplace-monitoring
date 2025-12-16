"""
RTSP stream handler.
"""
import cv2
from typing import Optional, Iterator
from pathlib import Path

from observability.logging import get_logger

logger = get_logger(__name__)


class RTSPHandler:
    """Handler for RTSP video streams."""
    
    def __init__(self, stream_url: str, timeout: int = 5):
        """
        Initialize RTSP handler.
        
        Args:
            stream_url: RTSP stream URL
            timeout: Connection timeout in seconds
        """
        self.stream_url = stream_url
        self.timeout = timeout
        self.cap: Optional[cv2.VideoCapture] = None
    
    def connect(self) -> bool:
        """
        Connect to RTSP stream.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.cap = cv2.VideoCapture(self.stream_url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce latency
            
            if not self.cap.isOpened():
                logger.error(f"Failed to open RTSP stream: {self.stream_url}")
                return False
            
            # Test read
            ret, frame = self.cap.read()
            if not ret:
                logger.error(f"Failed to read from RTSP stream: {self.stream_url}")
                self.cap.release()
                self.cap = None
                return False
            
            logger.info(f"Connected to RTSP stream: {self.stream_url}")
            return True
        
        except Exception as e:
            logger.error(f"Error connecting to RTSP stream: {e}")
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
            logger.error(f"Error reading frame from RTSP stream: {e}")
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
            logger.info(f"Disconnected from RTSP stream: {self.stream_url}")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

