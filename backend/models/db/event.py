"""
Event database model.
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.db.base import BaseModel
from models.enums import EventType, EventSeverity


class Event(BaseModel):
    """Event model for detected incidents."""
    
    __tablename__ = "events"
    
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    event_code = Column(String, nullable=False, index=True)  # e.g., "missing_helmet"
    severity = Column(String, default=EventSeverity.MEDIUM.value, nullable=False)
    confidence = Column(Float, nullable=False)  # Detection confidence score
    timestamp = Column(DateTime, nullable=False, index=True)
    frame_number = Column(Integer, nullable=True)
    clip_path = Column(String, nullable=True)  # Path to event clip
    metadata = Column(JSON, nullable=True)  # Detection metadata, bounding boxes, etc.
    description = Column(Text, nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationships
    # camera = relationship("Camera", back_populates="events")

