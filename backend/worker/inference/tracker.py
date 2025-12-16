"""
Object tracking implementation for multi-frame analysis.
"""
from typing import List, Dict, Any, Optional
import numpy as np
from collections import defaultdict

from observability.logging import get_logger

logger = get_logger(__name__)


class ObjectTracker:
    """Simple object tracker using IoU-based matching."""
    
    def __init__(self, max_disappeared: int = 5, iou_threshold: float = 0.3):
        """
        Initialize object tracker.
        
        Args:
            max_disappeared: Maximum frames an object can be missing before removal
            iou_threshold: IoU threshold for matching detections to tracks
        """
        self.max_disappeared = max_disappeared
        self.iou_threshold = iou_threshold
        self.tracks: Dict[int, Dict[str, Any]] = {}
        self.next_id = 1
    
    def _calculate_iou(self, bbox1: List[float], bbox2: List[float]) -> float:
        """
        Calculate Intersection over Union (IoU) of two bounding boxes.
        
        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]
            
        Returns:
            IoU value (0-1)
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # Calculate intersection
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i <= x1_i or y2_i <= y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # Calculate union
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def update(
        self,
        detections: List[Dict[str, Any]],
        frame_number: int,
    ) -> List[Dict[str, Any]]:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detection dictionaries with 'bbox'
            frame_number: Current frame number
            
        Returns:
            List of tracked objects with track IDs
        """
        if not detections:
            # No detections, increment disappeared count for all tracks
            for track_id in list(self.tracks.keys()):
                self.tracks[track_id]["disappeared"] += 1
                if self.tracks[track_id]["disappeared"] > self.max_disappeared:
                    del self.tracks[track_id]
            return []
        
        # Match detections to existing tracks
        matched_tracks = set()
        tracked_objects = []
        
        for detection in detections:
            best_match_id = None
            best_iou = 0.0
            
            for track_id, track in self.tracks.items():
                if track_id in matched_tracks:
                    continue
                
                iou = self._calculate_iou(detection["bbox"], track["bbox"])
                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_match_id = track_id
            
            if best_match_id is not None:
                # Update existing track
                track = self.tracks[best_match_id]
                track["bbox"] = detection["bbox"]
                track["last_seen"] = frame_number
                track["disappeared"] = 0
                track["detection_count"] += 1
                track.update({k: v for k, v in detection.items() if k != "bbox"})
                matched_tracks.add(best_match_id)
                
                tracked_objects.append({
                    **detection,
                    "track_id": best_match_id,
                    "track_age": frame_number - track["first_seen"],
                })
            else:
                # Create new track
                track_id = self.next_id
                self.next_id += 1
                
                self.tracks[track_id] = {
                    "bbox": detection["bbox"],
                    "first_seen": frame_number,
                    "last_seen": frame_number,
                    "disappeared": 0,
                    "detection_count": 1,
                    **{k: v for k, v in detection.items() if k != "bbox"},
                }
                
                tracked_objects.append({
                    **detection,
                    "track_id": track_id,
                    "track_age": 0,
                })
        
        # Increment disappeared count for unmatched tracks
        for track_id in list(self.tracks.keys()):
            if track_id not in matched_tracks:
                self.tracks[track_id]["disappeared"] += 1
                if self.tracks[track_id]["disappeared"] > self.max_disappeared:
                    del self.tracks[track_id]
        
        return tracked_objects
    
    def get_active_tracks(self) -> List[Dict[str, Any]]:
        """
        Get all active tracks.
        
        Returns:
            List of active track dictionaries
        """
        return [
            {
                "track_id": track_id,
                **track,
            }
            for track_id, track in self.tracks.items()
        ]
    
    def reset(self):
        """Reset tracker (clear all tracks)."""
        self.tracks = {}
        self.next_id = 1
        logger.debug("Tracker reset")

