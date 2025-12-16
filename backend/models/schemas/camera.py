"""
Camera schemas.
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from models.enums import CameraStatus


class CameraBase(BaseModel):
    """Base camera schema."""
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    stream_url: Optional[str] = None
    stream_type: str  # rtsp, http, file
    zone_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraCreate(CameraBase):
    """Camera creation schema."""
    pass


class CameraUpdate(BaseModel):
    """Camera update schema."""
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    stream_url: Optional[str] = None
    status: Optional[CameraStatus] = None
    zone_config: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class CameraResponse(CameraBase):
    """Camera response schema."""
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

