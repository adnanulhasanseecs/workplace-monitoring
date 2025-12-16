"""
Unit tests for video chunker.
"""
import sys
from pathlib import Path
import pytest
import cv2
import numpy as np
from tempfile import TemporaryDirectory

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from ingestion.chunker import VideoChunker


def create_test_video(output_path: Path, duration_seconds: float = 10.0, fps: float = 30.0):
    """Create a test video file."""
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    num_frames = int(duration_seconds * fps)
    for i in range(num_frames):
        frame = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        out.write(frame)
    
    out.release()


def test_chunker_initialization():
    """Test chunker initialization."""
    chunker = VideoChunker(chunk_duration_seconds=60)
    assert chunker.chunk_duration == 60
    assert chunker.output_dir.exists()


def test_chunk_file(tmp_path):
    """Test video file chunking."""
    # Create test video (10 seconds at 30 fps = 300 frames)
    test_video = tmp_path / "test_video.mp4"
    create_test_video(test_video, duration_seconds=10.0, fps=30.0)
    
    chunker = VideoChunker(
        chunk_duration_seconds=5.0,  # 5 second chunks
        output_dir=tmp_path / "chunks",
    )
    
    chunks = list(chunker.chunk_file(test_video, camera_id=1, job_id="test_job"))
    
    # Should create 2 chunks (10 seconds / 5 seconds per chunk)
    assert len(chunks) == 2
    
    # Verify chunks exist
    for chunk_path, metadata in chunks:
        assert chunk_path.exists()
        assert metadata["frames"] > 0
        assert "duration_seconds" in metadata


def test_get_chunk_count(tmp_path):
    """Test chunk count calculation."""
    test_video = tmp_path / "test_video.mp4"
    create_test_video(test_video, duration_seconds=10.0, fps=30.0)
    
    chunker = VideoChunker(chunk_duration_seconds=5.0)
    count = chunker.get_chunk_count(test_video)
    
    assert count == 2  # 10 seconds / 5 seconds per chunk

