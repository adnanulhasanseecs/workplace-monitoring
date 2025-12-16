"""
Pydantic schemas package.
"""
from models.schemas.auth import Token, TokenData, LoginRequest, UserCreate, UserResponse
from models.schemas.camera import CameraBase, CameraCreate, CameraUpdate, CameraResponse
from models.schemas.event import EventBase, EventCreate, EventResponse, EventFilter
from models.schemas.alert import AlertBase, AlertCreate, AlertResponse
from models.schemas.rule import RuleBase, RuleCreate, RuleUpdate, RuleResponse

__all__ = [
    "Token",
    "TokenData",
    "LoginRequest",
    "UserCreate",
    "UserResponse",
    "CameraBase",
    "CameraCreate",
    "CameraUpdate",
    "CameraResponse",
    "EventBase",
    "EventCreate",
    "EventResponse",
    "EventFilter",
    "AlertBase",
    "AlertCreate",
    "AlertResponse",
    "RuleBase",
    "RuleCreate",
    "RuleUpdate",
    "RuleResponse",
]

