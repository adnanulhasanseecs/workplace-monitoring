"""
Camera domain service - business logic layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models.db.camera import Camera
from models.enums import CameraStatus
from models.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from domain.cameras.repository import CameraRepository
from observability.logging import get_logger

logger = get_logger(__name__)


class CameraService:
    """Service for camera business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize camera service.
        
        Args:
            db: Database session
        """
        self.repository = CameraRepository(db)
        self.db = db
    
    def create_camera(self, camera_data: CameraCreate) -> CameraResponse:
        """
        Create a new camera with validation.
        
        Args:
            camera_data: Camera creation data
            
        Returns:
            Created camera response
            
        Raises:
            ValueError: If camera name or stream URL already exists
        """
        # Check for duplicate name
        existing = self.repository.get_by_name(camera_data.name)
        if existing:
            raise ValueError(f"Camera with name '{camera_data.name}' already exists")
        
        # Check for duplicate stream URL if provided
        if camera_data.stream_url:
            existing = self.repository.get_by_stream_url(camera_data.stream_url)
            if existing:
                raise ValueError(f"Camera with stream URL '{camera_data.stream_url}' already exists")
        
        camera = self.repository.create(camera_data)
        logger.info("Camera created", extra={"camera_id": camera.id, "name": camera.name})
        return CameraResponse.model_validate(camera)
    
    def get_camera(self, camera_id: int) -> Optional[CameraResponse]:
        """
        Get camera by ID.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Camera response or None if not found
        """
        camera = self.repository.get_by_id(camera_id)
        if not camera:
            return None
        return CameraResponse.model_validate(camera)
    
    def list_cameras(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CameraStatus] = None,
        location: Optional[str] = None,
    ) -> List[CameraResponse]:
        """
        List cameras with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            location: Filter by location
            
        Returns:
            List of camera responses
        """
        cameras = self.repository.get_all(skip=skip, limit=limit, status=status, location=location)
        return [CameraResponse.model_validate(camera) for camera in cameras]
    
    def update_camera(self, camera_id: int, camera_data: CameraUpdate) -> Optional[CameraResponse]:
        """
        Update camera with validation.
        
        Args:
            camera_id: Camera ID
            camera_data: Camera update data
            
        Returns:
            Updated camera response or None if not found
            
        Raises:
            ValueError: If new name or stream URL conflicts with existing camera
        """
        # Check if camera exists
        existing = self.repository.get_by_id(camera_id)
        if not existing:
            return None
        
        # Check for duplicate name if name is being updated
        if camera_data.name and camera_data.name != existing.name:
            duplicate = self.repository.get_by_name(camera_data.name)
            if duplicate:
                raise ValueError(f"Camera with name '{camera_data.name}' already exists")
        
        # Check for duplicate stream URL if stream URL is being updated
        if camera_data.stream_url and camera_data.stream_url != existing.stream_url:
            duplicate = self.repository.get_by_stream_url(camera_data.stream_url)
            if duplicate:
                raise ValueError(f"Camera with stream URL '{camera_data.stream_url}' already exists")
        
        camera = self.repository.update(camera_id, camera_data)
        if camera:
            logger.info("Camera updated", extra={"camera_id": camera.id, "name": camera.name})
            return CameraResponse.model_validate(camera)
        return None
    
    def delete_camera(self, camera_id: int) -> bool:
        """
        Delete camera.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if deleted, False if not found
        """
        camera = self.repository.get_by_id(camera_id)
        if not camera:
            return False
        
        success = self.repository.delete(camera_id)
        if success:
            logger.info("Camera deleted", extra={"camera_id": camera_id, "name": camera.name})
        return success
    
    def activate_camera(self, camera_id: int) -> Optional[CameraResponse]:
        """
        Activate a camera.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Updated camera response or None if not found
        """
        camera = self.repository.update(
            camera_id,
            CameraUpdate(status=CameraStatus.ACTIVE)
        )
        if camera:
            logger.info("Camera activated", extra={"camera_id": camera.id})
            return CameraResponse.model_validate(camera)
        return None
    
    def deactivate_camera(self, camera_id: int) -> Optional[CameraResponse]:
        """
        Deactivate a camera.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Updated camera response or None if not found
        """
        camera = self.repository.update(
            camera_id,
            CameraUpdate(status=CameraStatus.INACTIVE)
        )
        if camera:
            logger.info("Camera deactivated", extra={"camera_id": camera.id})
            return CameraResponse.model_validate(camera)
        return None
    
    def get_camera_count(self, status: Optional[CameraStatus] = None) -> int:
        """
        Get total camera count.
        
        Args:
            status: Filter by status
            
        Returns:
            Number of cameras
        """
        return self.repository.count(status=status)

