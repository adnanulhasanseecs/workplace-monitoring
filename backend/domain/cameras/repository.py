"""
Camera repository - data access layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from models.db.camera import Camera
from models.enums import CameraStatus
from models.schemas.camera import CameraCreate, CameraUpdate


class CameraRepository:
    """Repository for camera data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize camera repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, camera_data: CameraCreate) -> Camera:
        """
        Create a new camera.
        
        Args:
            camera_data: Camera creation data
            
        Returns:
            Created camera instance
        """
        camera = Camera(
            name=camera_data.name,
            description=camera_data.description,
            location=camera_data.location,
            stream_url=camera_data.stream_url,
            stream_type=camera_data.stream_type,
            zone_config=camera_data.zone_config,
            extra_metadata=camera_data.extra_metadata,
            status=CameraStatus.INACTIVE.value,
        )
        self.db.add(camera)
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def get_by_id(self, camera_id: int) -> Optional[Camera]:
        """
        Get camera by ID.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Camera instance or None if not found
        """
        return self.db.query(Camera).filter(Camera.id == camera_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[CameraStatus] = None,
        location: Optional[str] = None,
    ) -> List[Camera]:
        """
        Get all cameras with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            location: Filter by location
            
        Returns:
            List of camera instances
        """
        query = self.db.query(Camera)
        
        if status:
            query = query.filter(Camera.status == status.value)
        
        if location:
            query = query.filter(Camera.location == location)
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, camera_id: int, camera_data: CameraUpdate) -> Optional[Camera]:
        """
        Update camera.
        
        Args:
            camera_id: Camera ID
            camera_data: Camera update data
            
        Returns:
            Updated camera instance or None if not found
        """
        camera = self.get_by_id(camera_id)
        if not camera:
            return None
        
        update_data = camera_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(camera, field, value)
        
        self.db.commit()
        self.db.refresh(camera)
        return camera
    
    def delete(self, camera_id: int) -> bool:
        """
        Delete camera.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if deleted, False if not found
        """
        camera = self.get_by_id(camera_id)
        if not camera:
            return False
        
        self.db.delete(camera)
        self.db.commit()
        return True
    
    def get_by_name(self, name: str) -> Optional[Camera]:
        """
        Get camera by name.
        
        Args:
            name: Camera name
            
        Returns:
            Camera instance or None if not found
        """
        return self.db.query(Camera).filter(Camera.name == name).first()
    
    def get_by_stream_url(self, stream_url: str) -> Optional[Camera]:
        """
        Get camera by stream URL.
        
        Args:
            stream_url: Stream URL
            
        Returns:
            Camera instance or None if not found
        """
        return self.db.query(Camera).filter(Camera.stream_url == stream_url).first()
    
    def count(self, status: Optional[CameraStatus] = None) -> int:
        """
        Count cameras.
        
        Args:
            status: Filter by status
            
        Returns:
            Number of cameras
        """
        query = self.db.query(Camera)
        if status:
            query = query.filter(Camera.status == status.value)
        return query.count()

