"""
Camera database model.
"""
from sqlalchemy import Column, String, Integer, JSON, Text
from sqlalchemy.orm import relationship

from models.db.base import BaseModel
from models.enums import CameraStatus


class Camera(BaseModel):
    """Camera model for video sources."""
    
    __tablename__ = "cameras"
    
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    location = Column(String, nullable=True)
    stream_url = Column(String, nullable=True)  # RTSP or HTTP URL
    stream_type = Column(String, nullable=False)  # rtsp, http, file
    status = Column(String, default=CameraStatus.INACTIVE.value, nullable=False)
    zone_config = Column(JSON, nullable=True)  # Zone definitions for this camera
    extra_metadata = Column(JSON, nullable=True)  # Additional metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    
    # Relationships
    # events = relationship("Event", back_populates="camera")

