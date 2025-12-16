"""
Alert schemas.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from models.enums import AlertStatus, NotificationChannel


class AlertBase(BaseModel):
    """Base alert schema."""
    event_id: Optional[int] = None
    alert_rule_id: Optional[int] = None
    channel: NotificationChannel
    recipient: str
    subject: Optional[str] = None
    message: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    """Alert creation schema."""
    pass


class AlertResponse(AlertBase):
    """Alert response schema."""
    id: int
    status: str
    sent_at: Optional[datetime] = None
    acknowledged: bool
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

