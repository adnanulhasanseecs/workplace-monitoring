"""
User database model.
"""
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from models.db.base import BaseModel
from models.enums import UserRole


class User(BaseModel):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, default=UserRole.VIEWER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    # audit_logs = relationship("AuditLog", back_populates="user")

