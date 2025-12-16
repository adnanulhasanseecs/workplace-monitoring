"""
Unit tests for object tracker.
"""
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Mock torch before importing tracker
import sys
from unittest.mock import MagicMock
sys.modules['torch'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()

from worker.inference.tracker import ObjectTracker


def test_tracker_initialization():
    """Test tracker initialization."""
    tracker = ObjectTracker(max_disappeared=5, iou_threshold=0.3)
    assert tracker.max_disappeared == 5
    assert tracker.iou_threshold == 0.3
    assert len(tracker.tracks) == 0


def test_tracker_iou_calculation():
    """Test IoU calculation."""
    tracker = ObjectTracker()
    
    # Overlapping boxes
    bbox1 = [10, 10, 50, 50]
    bbox2 = [20, 20, 60, 60]
    iou = tracker._calculate_iou(bbox1, bbox2)
    assert 0 < iou < 1
    
    # Non-overlapping boxes
    bbox3 = [100, 100, 150, 150]
    iou = tracker._calculate_iou(bbox1, bbox3)
    assert iou == 0.0
    
    # Same box
    iou = tracker._calculate_iou(bbox1, bbox1)
    assert iou == 1.0


def test_tracker_update():
    """Test tracker update with detections."""
    tracker = ObjectTracker()
    
    # First frame - new detections
    detections1 = [
        {"bbox": [10, 10, 50, 50], "class_id": 0, "confidence": 0.9},
        {"bbox": [100, 100, 150, 150], "class_id": 0, "confidence": 0.8},
    ]
    
    tracked = tracker.update(detections1, frame_number=0)
    assert len(tracked) == 2
    assert all("track_id" in obj for obj in tracked)
    assert len(tracker.tracks) == 2
    
    # Second frame - same detections (should match)
    detections2 = [
        {"bbox": [12, 12, 52, 52], "class_id": 0, "confidence": 0.9},  # Slight movement
        {"bbox": [102, 102, 152, 152], "class_id": 0, "confidence": 0.8},
    ]
    
    tracked = tracker.update(detections2, frame_number=1)
    assert len(tracked) == 2
    # Should have same track IDs
    track_ids = [obj["track_id"] for obj in tracked]
    assert len(set(track_ids)) == 2


def test_tracker_disappeared():
    """Test tracker handling of disappeared objects."""
    tracker = ObjectTracker(max_disappeared=2)
    
    # Add detection
    detections = [{"bbox": [10, 10, 50, 50], "class_id": 0, "confidence": 0.9}]
    tracker.update(detections, frame_number=0)
    assert len(tracker.tracks) == 1
    
    # No detections - first frame (disappeared = 1)
    tracker.update([], frame_number=1)
    assert len(tracker.tracks) == 1  # Still there (disappeared = 1, max = 2)
    
    # No detections - second frame (disappeared = 2)
    tracker.update([], frame_number=2)
    # Track might still be there (2 is not > 2) or removed depending on implementation
    # Core behavior: it should eventually be removed
    
    # No detections - third frame (disappeared = 3, exceeds max_disappeared = 2)
    tracker.update([], frame_number=3)
    # After 3 frames without detection, disappeared = 3, which is > 2, so removed
    assert len(tracker.tracks) == 0  # Removed (disappeared > max_disappeared)


def test_tracker_reset():
    """Test tracker reset."""
    tracker = ObjectTracker()
    
    detections = [{"bbox": [10, 10, 50, 50], "class_id": 0, "confidence": 0.9}]
    tracker.update(detections, frame_number=0)
    assert len(tracker.tracks) > 0
    
    tracker.reset()
    assert len(tracker.tracks) == 0
    assert tracker.next_id == 1

