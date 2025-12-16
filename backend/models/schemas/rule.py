"""
Rule schemas.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime


class RuleBase(BaseModel):
    """Base rule schema."""
    name: str
    description: Optional[str] = None
    event_code: str
    event_type: str
    is_active: bool = True
    confidence_threshold: float = 0.5
    camera_ids: Optional[List[int]] = None
    zone_config: Optional[Dict[str, Any]] = None
    conditions: Dict[str, Any]
    alert_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class RuleCreate(RuleBase):
    """Rule creation schema."""
    pass


class RuleUpdate(BaseModel):
    """Rule update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    confidence_threshold: Optional[float] = None
    camera_ids: Optional[List[int]] = None
    zone_config: Optional[Dict[str, Any]] = None
    conditions: Optional[Dict[str, Any]] = None
    alert_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class RuleResponse(RuleBase):
    """Rule response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

