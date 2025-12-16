"""
Alert database model.
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.db.base import BaseModel
from models.enums import AlertStatus, NotificationChannel


class Alert(BaseModel):
    """Alert model for notifications."""
    
    __tablename__ = "alerts"
    
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    alert_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True)
    status = Column(String, default=AlertStatus.PENDING.value, nullable=False)
    channel = Column(String, nullable=False)  # email, webhook, in_app
    recipient = Column(String, nullable=False)  # email address, webhook URL, user ID
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    acknowledged = Column(Boolean, default=False, nullable=False)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # Relationships
    # event = relationship("Event", back_populates="alerts")

