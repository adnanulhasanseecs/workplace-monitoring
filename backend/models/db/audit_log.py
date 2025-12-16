"""
Audit log database model.
"""
from sqlalchemy import Column, String, Integer, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship

from models.db.base import BaseModel


class AuditLog(BaseModel):
    """Audit log model for compliance and tracking."""
    
    __tablename__ = "audit_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)  # e.g., "user.login", "camera.create"
    resource_type = Column(String, nullable=True)  # e.g., "user", "camera", "rule"
    resource_id = Column(Integer, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=True)  # Additional action details
    status = Column(String, nullable=False)  # success, failure
    error_message = Column(Text, nullable=True)
    
    # Relationships
    # user = relationship("User", back_populates="audit_logs")

