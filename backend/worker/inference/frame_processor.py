"""
Frame processing pipeline for video analysis.
"""
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from worker.inference.yolo_engine import YOLO11Engine
from observability.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class FrameProcessor:
    """Frame processing pipeline for video analysis."""
    
    def __init__(self, yolo_engine: Optional[YOLO11Engine] = None):
        """
        Initialize frame processor.
        
        Args:
            yolo_engine: YOLO11 engine instance (creates new if None)
        """
        self.yolo_engine = yolo_engine or YOLO11Engine()
        if not self.yolo_engine.model:
            self.yolo_engine.load_model()
        
        self.base_fps = settings.DEFAULT_FPS
        self.burst_fps = settings.BURST_FPS
        self.frame_sample_rate = settings.FRAME_SAMPLE_RATE
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        timestamp: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Process a single frame.
        
        Args:
            frame: Frame image (numpy array)
            frame_number: Frame number in sequence
            timestamp: Optional timestamp
            
        Returns:
            Dictionary with detections and metadata
        """
        # Run YOLO11 inference
        results = self.yolo_engine.detect(frame)
        
        # Format detections
        detections = []
        for detection in results:
            detections.append({
                "class_id": int(detection["class_id"]),
                "class_name": detection["class_name"],
                "confidence": float(detection["confidence"]),
                "bbox": detection["bbox"],  # [x1, y1, x2, y2]
                "center": detection.get("center"),  # [cx, cy]
            })
        
        return {
            "frame_number": frame_number,
            "timestamp": timestamp,
            "detections": detections,
            "detection_count": len(detections),
        }
    
    def process_frame_batch(
        self,
        frames: List[np.ndarray],
        start_frame: int = 0,
        timestamps: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of frames (more efficient).
        
        Args:
            frames: List of frame images
            start_frame: Starting frame number
            timestamps: Optional list of timestamps
            
        Returns:
            List of frame processing results
        """
        if not frames:
            return []
        
        # Batch inference if supported
        results = []
        for i, frame in enumerate(frames):
            frame_number = start_frame + i
            timestamp = timestamps[i] if timestamps and i < len(timestamps) else None
            
            result = self.process_frame(frame, frame_number, timestamp)
            results.append(result)
        
        logger.debug(f"Processed batch of {len(frames)} frames")
        return results
    
    def should_sample_frame(self, frame_number: int, event_detected: bool = False) -> bool:
        """
        Determine if frame should be sampled.
        
        Args:
            frame_number: Frame number
            event_detected: Whether an event was detected in recent frames
            
        Returns:
            True if frame should be processed
        """
        if event_detected:
            # Use burst FPS when events detected
            return frame_number % (30 // self.burst_fps) == 0
        else:
            # Use base FPS for normal processing
            return frame_number % (30 // self.base_fps) == 0
    
    def extract_frame_from_video(
        self,
        video_path: Path,
        frame_number: int,
    ) -> Optional[np.ndarray]:
        """
        Extract a specific frame from video.
        
        Args:
            video_path: Path to video file
            frame_number: Frame number to extract
            
        Returns:
            Frame as numpy array or None if extraction failed
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            logger.warning(f"Failed to extract frame {frame_number} from {video_path}")
            return None
        
        return frame

