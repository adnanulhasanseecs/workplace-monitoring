"""
Unit tests for Pydantic schemas.
"""
import sys
from pathlib import Path
import pytest
from datetime import datetime
from pydantic import ValidationError

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models.schemas.auth import UserCreate, UserResponse, LoginRequest, Token
from models.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from models.schemas.event import EventCreate, EventResponse, EventFilter
from models.schemas.alert import AlertCreate, AlertResponse
from models.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from models.enums import UserRole, EventSeverity, AlertStatus, CameraStatus, NotificationChannel


def test_user_create_schema():
    """Test UserCreate schema validation."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "role": UserRole.ADMIN,
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.role == UserRole.ADMIN


def test_user_create_schema_invalid_email():
    """Test UserCreate schema with invalid email."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            username="testuser",
            password="TestPassword123!",
        )


def test_login_request_schema():
    """Test LoginRequest schema."""
    login = LoginRequest(username="testuser", password="password123")
    assert login.username == "testuser"
    assert login.password == "password123"


def test_camera_create_schema():
    """Test CameraCreate schema."""
    camera_data = {
        "name": "Test Camera",
        "description": "Test description",
        "stream_type": "rtsp",
        "stream_url": "rtsp://example.com/stream",
    }
    camera = CameraCreate(**camera_data)
    assert camera.name == "Test Camera"
    assert camera.stream_type == "rtsp"


def test_camera_update_schema():
    """Test CameraUpdate schema (all fields optional)."""
    camera_update = CameraUpdate(name="Updated Name")
    assert camera_update.name == "Updated Name"
    assert camera_update.description is None


def test_event_create_schema():
    """Test EventCreate schema."""
    event_data = {
        "camera_id": 1,
        "event_type": "ppe_violation",
        "event_code": "missing_helmet",
        "severity": EventSeverity.HIGH,
        "confidence": 0.95,
        "timestamp": datetime.utcnow(),
    }
    event = EventCreate(**event_data)
    assert event.event_code == "missing_helmet"
    assert event.confidence == 0.95


def test_event_filter_schema():
    """Test EventFilter schema."""
    event_filter = EventFilter(
        camera_id=1,
        event_type="ppe_violation",
        severity=EventSeverity.HIGH,
        limit=50,
        offset=0,
    )
    assert event_filter.camera_id == 1
    assert event_filter.limit == 50


def test_alert_create_schema():
    """Test AlertCreate schema."""
    alert_data = {
        "channel": NotificationChannel.EMAIL,
        "recipient": "admin@example.com",
        "subject": "Test Alert",
        "message": "Test message",
    }
    alert = AlertCreate(**alert_data)
    assert alert.channel == NotificationChannel.EMAIL
    assert alert.recipient == "admin@example.com"


def test_rule_create_schema():
    """Test RuleCreate schema."""
    rule_data = {
        "name": "Test Rule",
        "event_code": "missing_helmet",
        "event_type": "ppe_violation",
        "confidence_threshold": 0.7,
        "conditions": {"class": "person"},
    }
    rule = RuleCreate(**rule_data)
    assert rule.name == "Test Rule"
    assert rule.confidence_threshold == 0.7
    assert rule.conditions == {"class": "person"}


def test_rule_update_schema():
    """Test RuleUpdate schema (all fields optional)."""
    rule_update = RuleUpdate(name="Updated Rule", is_active=False)
    assert rule_update.name == "Updated Rule"
    assert rule_update.is_active is False

