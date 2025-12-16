"""
Event clip extraction - saves only event clips, not full video.
"""
import cv2
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from observability.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class ClipExtractor:
    """Extract and save event clips from video."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize clip extractor.
        
        Args:
            output_dir: Directory to save event clips (defaults to config)
        """
        self.output_dir = Path(output_dir) if output_dir else Path(settings.EVENT_CLIPS_PATH)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_clip(
        self,
        video_path: Path,
        start_frame: int,
        end_frame: int,
        event_id: int,
        camera_id: int,
        padding_seconds: float = 5.0,
    ) -> Optional[Path]:
        """
        Extract event clip from video.
        
        Args:
            video_path: Path to source video
            start_frame: Start frame number
            end_frame: End frame number
            event_id: Event ID
            camera_id: Camera ID
            padding_seconds: Seconds to add before and after event
            
        Returns:
            Path to extracted clip or None if extraction failed
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video: {video_path}")
            return None
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Calculate padding frames
        padding_frames = int(fps * padding_seconds)
        clip_start = max(0, start_frame - padding_frames)
        clip_end = min(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), end_frame + padding_frames)
        
        # Generate clip filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        clip_filename = f"event_{event_id}_camera_{camera_id}_{timestamp}.mp4"
        clip_path = self.output_dir / clip_filename
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))
        
        # Seek to start
        cap.set(cv2.CAP_PROP_POS_FRAMES, clip_start)
        
        frames_written = 0
        for frame_num in range(clip_start, clip_end):
            ret, frame = cap.read()
            if not ret:
                break
            
            out.write(frame)
            frames_written += 1
        
        out.release()
        cap.release()
        
        if frames_written == 0:
            logger.warning(f"No frames extracted for event {event_id}")
            if clip_path.exists():
                clip_path.unlink()
            return None
        
        logger.info(
            f"Extracted clip: {clip_filename}, "
            f"frames={frames_written}, duration={frames_written/fps:.2f}s"
        )
        
        return clip_path
    
    def extract_clips_from_events(
        self,
        video_path: Path,
        events: List[dict],  # List of event dicts with frame_number
        camera_id: int,
    ) -> List[Tuple[int, Path]]:
        """
        Extract multiple clips from events in a video.
        
        Args:
            video_path: Path to source video
            events: List of event dictionaries with 'id' and 'frame_number'
            camera_id: Camera ID
            
        Returns:
            List of tuples (event_id, clip_path)
        """
        extracted_clips = []
        
        for event in events:
            event_id = event.get('id')
            frame_number = event.get('frame_number')
            
            if not event_id or frame_number is None:
                continue
            
            # Extract clip around event (5 seconds before/after)
            clip_path = self.extract_clip(
                video_path=video_path,
                start_frame=frame_number,
                end_frame=frame_number,
                event_id=event_id,
                camera_id=camera_id,
                padding_seconds=5.0,
            )
            
            if clip_path:
                extracted_clips.append((event_id, clip_path))
        
        logger.info(f"Extracted {len(extracted_clips)} clips from {len(events)} events")
        return extracted_clips

