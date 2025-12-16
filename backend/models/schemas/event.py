"""
Event schemas.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from models.enums import EventType, EventSeverity


class EventBase(BaseModel):
    """Base event schema."""
    camera_id: int
    event_type: str
    event_code: str
    severity: EventSeverity
    confidence: float
    timestamp: datetime
    frame_number: Optional[int] = None
    clip_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class EventCreate(EventBase):
    """Event creation schema."""
    pass


class EventResponse(EventBase):
    """Event response schema."""
    id: int
    acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EventFilter(BaseModel):
    """Event filter schema for queries."""
    camera_id: Optional[int] = None
    event_type: Optional[str] = None
    event_code: Optional[str] = None
    severity: Optional[EventSeverity] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    acknowledged: Optional[bool] = None
    limit: int = 100
    offset: int = 0

