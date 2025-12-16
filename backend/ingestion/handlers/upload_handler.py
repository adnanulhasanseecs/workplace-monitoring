"""
File upload handler.
"""
import shutil
from pathlib import Path
from typing import Optional
from fastapi import UploadFile

from observability.logging import get_logger
from ingestion.validator import VideoValidator

logger = get_logger(__name__)


class UploadHandler:
    """Handler for video file uploads."""
    
    def __init__(self, upload_dir: Path):
        """
        Initialize upload handler.
        
        Args:
            upload_dir: Directory to save uploaded files
        """
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_upload(self, file: UploadFile, filename: Optional[str] = None) -> Path:
        """
        Save uploaded file to disk.
        
        Args:
            file: FastAPI UploadFile object
            filename: Optional custom filename (defaults to original filename)
            
        Returns:
            Path to saved file
            
        Raises:
            ValueError: If file validation fails
        """
        if not filename:
            filename = file.filename
        
        if not filename:
            raise ValueError("Filename is required")
        
        file_path = self.upload_dir / filename
        
        # Validate file extension
        if file_path.suffix.lower() not in VideoValidator.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file format: {file_path.suffix}. "
                f"Supported: {', '.join(VideoValidator.SUPPORTED_EXTENSIONS)}"
            )
        
        try:
            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Validate saved file
            is_valid, error_msg = VideoValidator.validate_file_upload(file_path)
            if not is_valid:
                file_path.unlink()  # Delete invalid file
                raise ValueError(error_msg)
            
            logger.info(f"File uploaded successfully: {file_path}")
            return file_path
        
        except Exception as e:
            logger.error(f"Error saving uploaded file: {e}")
            if file_path.exists():
                file_path.unlink()
            raise
    
    def get_file_info(self, file_path: Path) -> Optional[dict]:
        """
        Get file information.
        
        Args:
            file_path: Path to video file
            
        Returns:
            Dictionary with file properties or None if unavailable
        """
        if not file_path.exists():
            return None
        
        try:
            stat = file_path.stat()
            return {
                "filename": file_path.name,
                "size": stat.st_size,
                "extension": file_path.suffix,
                "path": str(file_path),
            }
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None
    
    def delete_file(self, file_path: Path) -> bool:
        """
        Delete uploaded file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

