"""
Video ingestion service - main service for handling video inputs.
"""
from typing import Optional, List
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session

from models.db.camera import Camera
from models.enums import CameraStatus
from ingestion.validator import VideoValidator
from ingestion.handlers.rtsp_handler import RTSPHandler
from ingestion.handlers.http_handler import HTTPHandler
from ingestion.handlers.upload_handler import UploadHandler
from ingestion.chunker import VideoChunker
from observability.logging import get_logger

logger = get_logger(__name__)


class IngestionService:
    """Service for video ingestion operations."""
    
    def __init__(self, db: Session, upload_dir: Optional[Path] = None):
        """
        Initialize ingestion service.
        
        Args:
            db: Database session
            upload_dir: Directory for uploaded files
        """
        self.db = db
        self.upload_dir = Path(upload_dir) if upload_dir else Path("./storage/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.validator = VideoValidator()
        self.chunker = VideoChunker()
    
    def validate_camera_stream(self, camera: Camera) -> tuple[bool, Optional[str]]:
        """
        Validate camera stream configuration.
        
        Args:
            camera: Camera instance
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not camera.stream_url:
            return False, "Camera stream URL is not configured"
        
        return self.validator.validate_stream_url(camera.stream_url, camera.stream_type)
    
    async def handle_file_upload(
        self,
        file: UploadFile,
        camera_id: int,
        job_id: Optional[str] = None,
    ) -> tuple[Path, List[tuple[Path, dict]]]:
        """
        Handle file upload and create chunks.
        
        Args:
            file: Uploaded file
            camera_id: Camera ID
            job_id: Optional job ID
            
        Returns:
            Tuple of (uploaded_file_path, list of (chunk_path, chunk_metadata))
            
        Raises:
            ValueError: If validation fails
        """
        upload_handler = UploadHandler(self.upload_dir)
        
        # Save uploaded file
        file_path = await upload_handler.save_upload(file)
        
        # Validate file
        is_valid, error_msg = self.validator.validate_file_upload(file_path)
        if not is_valid:
            upload_handler.delete_file(file_path)
            raise ValueError(error_msg)
        
        # Create chunks
        chunks = list(self.chunker.chunk_file(file_path, camera_id, job_id))
        
        logger.info(
            f"File uploaded and chunked: {file_path.name}, "
            f"camera_id={camera_id}, chunks={len(chunks)}"
        )
        
        return file_path, chunks
    
    def get_stream_handler(self, camera: Camera):
        """
        Get appropriate stream handler for camera.
        
        Args:
            camera: Camera instance
            
        Returns:
            Stream handler instance (RTSPHandler or HTTPHandler)
            
        Raises:
            ValueError: If stream type is unsupported
        """
        if camera.stream_type == "rtsp":
            return RTSPHandler(camera.stream_url)
        elif camera.stream_type == "http":
            return HTTPHandler(camera.stream_url)
        else:
            raise ValueError(f"Unsupported stream type: {camera.stream_type}")
    
    def test_stream_connection(self, camera: Camera) -> tuple[bool, Optional[str], Optional[dict]]:
        """
        Test connection to camera stream.
        
        Args:
            camera: Camera instance
            
        Returns:
            Tuple of (is_connected, error_message, stream_info)
        """
        # Validate stream URL first
        is_valid, error_msg = self.validate_camera_stream(camera)
        if not is_valid:
            return False, error_msg, None
        
        try:
            handler = self.get_stream_handler(camera)
            
            if handler.connect():
                stream_info = handler.get_stream_info()
                handler.disconnect()
                return True, None, stream_info
            else:
                return False, "Failed to connect to stream", None
        
        except Exception as e:
            logger.error(f"Error testing stream connection: {e}")
            return False, str(e), None
    
    def create_processing_job(
        self,
        camera_id: int,
        source_type: str,  # "stream" or "file"
        source_path: Optional[str] = None,
        job_metadata: Optional[dict] = None,
    ) -> dict:
        """
        Create a processing job for orchestrator.
        
        Args:
            camera_id: Camera ID
            source_type: Type of source ("stream" or "file")
            source_path: Path to source (for file uploads)
            job_metadata: Optional job metadata
            
        Returns:
            Job definition dictionary
        """
        job = {
            "camera_id": camera_id,
            "source_type": source_type,
            "source_path": source_path,
            "metadata": job_metadata or {},
            "status": "pending",
            "created_at": None,  # Will be set by orchestrator
        }
        
        logger.info(f"Created processing job: camera_id={camera_id}, type={source_type}")
        return job

