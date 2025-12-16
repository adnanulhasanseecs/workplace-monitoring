"""
Video chunking logic for processing.
"""
import cv2
from pathlib import Path
from typing import Optional, Iterator, Tuple
from datetime import datetime, timedelta

from observability.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class VideoChunker:
    """Video chunker for splitting videos into processable segments."""
    
    def __init__(
        self,
        chunk_duration_seconds: Optional[int] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize video chunker.
        
        Args:
            chunk_duration_seconds: Duration of each chunk in seconds (defaults to config)
            output_dir: Directory to save chunks (defaults to config)
        """
        self.chunk_duration = chunk_duration_seconds or settings.VIDEO_CHUNK_DURATION_SECONDS
        self.output_dir = Path(output_dir) if output_dir else Path(settings.VIDEO_STORAGE_PATH) / "chunks"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def chunk_file(
        self,
        input_path: Path,
        camera_id: int,
        job_id: Optional[str] = None,
    ) -> Iterator[Tuple[Path, dict]]:
        """
        Chunk a video file into segments.
        
        Args:
            input_path: Path to input video file
            camera_id: Camera ID
            job_id: Optional job ID for naming
            
        Yields:
            Tuples of (chunk_path, chunk_metadata)
        """
        cap = cv2.VideoCapture(str(input_path))
        
        if not cap.isOpened():
            logger.error(f"Failed to open video file: {input_path}")
            return
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frames_per_chunk = int(fps * self.chunk_duration)
        chunk_index = 0
        
        logger.info(
            f"Chunking video: {input_path.name}, "
            f"fps={fps:.2f}, duration={total_frames/fps:.2f}s, "
            f"chunk_duration={self.chunk_duration}s"
        )
        
        while True:
            chunk_filename = f"chunk_{camera_id}_{job_id or 'unknown'}_{chunk_index:04d}.mp4"
            chunk_path = self.output_dir / chunk_filename
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(chunk_path), fourcc, fps, (width, height))
            
            frames_written = 0
            start_frame = chunk_index * frames_per_chunk
            
            # Seek to start position
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            while frames_written < frames_per_chunk:
                ret, frame = cap.read()
                if not ret:
                    break
                
                out.write(frame)
                frames_written += 1
            
            out.release()
            
            if frames_written == 0:
                # No more frames, cleanup empty chunk
                if chunk_path.exists():
                    chunk_path.unlink()
                break
            
            chunk_metadata = {
                "chunk_index": chunk_index,
                "start_frame": start_frame,
                "end_frame": start_frame + frames_written - 1,
                "frames": frames_written,
                "duration_seconds": frames_written / fps if fps > 0 else 0,
                "fps": fps,
                "width": width,
                "height": height,
                "path": str(chunk_path),
            }
            
            logger.info(f"Created chunk {chunk_index}: {chunk_filename} ({frames_written} frames)")
            yield chunk_path, chunk_metadata
            
            chunk_index += 1
        
        cap.release()
    
    def get_chunk_count(self, video_path: Path) -> int:
        """
        Calculate number of chunks for a video.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Number of chunks
        """
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            return 0
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        
        if fps == 0:
            return 0
        
        frames_per_chunk = int(fps * self.chunk_duration)
        if frames_per_chunk == 0:
            return 0
        
        return (total_frames + frames_per_chunk - 1) // frames_per_chunk  # Ceiling division

