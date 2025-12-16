"""
Rule database model.
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, JSON, Text
from sqlalchemy.orm import relationship

from models.db.base import BaseModel


class Rule(BaseModel):
    """Rule model for event detection configuration."""
    
    __tablename__ = "rules"
    
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    event_code = Column(String, nullable=False, index=True)  # e.g., "missing_helmet"
    event_type = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    confidence_threshold = Column(Float, default=0.5, nullable=False)
    camera_ids = Column(JSON, nullable=True)  # List of camera IDs, null = all cameras
    zone_config = Column(JSON, nullable=True)  # Zone-specific rules
    conditions = Column(JSON, nullable=False)  # Rule evaluation conditions
    alert_config = Column(JSON, nullable=True)  # Alert configuration
    metadata = Column(JSON, nullable=True)

