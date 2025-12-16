"""
Unit tests for database models.
"""
import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models.db.user import User
from models.db.camera import Camera
from models.db.event import Event
from models.db.alert import Alert
from models.db.rule import Rule
from models.db.audit_log import AuditLog
from models.enums import UserRole, EventType, EventSeverity, AlertStatus, CameraStatus, NotificationChannel


def test_user_model(db_session):
    """Test User model creation."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
        full_name="Test User",
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.role == UserRole.ADMIN.value
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


def test_camera_model(db_session):
    """Test Camera model creation."""
    camera = Camera(
        name="Test Camera",
        description="Test camera description",
        location="Building A",
        stream_url="rtsp://example.com/stream",
        stream_type="rtsp",
        status=CameraStatus.ACTIVE.value,
    )
    db_session.add(camera)
    db_session.commit()
    db_session.refresh(camera)
    
    assert camera.id is not None
    assert camera.name == "Test Camera"
    assert camera.stream_type == "rtsp"
    assert camera.status == CameraStatus.ACTIVE.value


def test_event_model(db_session, test_user_data):
    """Test Event model creation."""
    # Create camera first
    camera = Camera(
        name="Test Camera",
        stream_type="rtsp",
        status=CameraStatus.ACTIVE.value,
    )
    db_session.add(camera)
    db_session.commit()
    
    event = Event(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH.value,
        confidence=0.95,
        timestamp=datetime.utcnow(),
        frame_number=100,
        clip_path="/storage/clips/event_1.mp4",
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    assert event.id is not None
    assert event.camera_id == camera.id
    assert event.event_code == "missing_helmet"
    assert event.confidence == 0.95
    assert event.acknowledged is False


def test_alert_model(db_session):
    """Test Alert model creation."""
    alert = Alert(
        channel=NotificationChannel.EMAIL.value,
        recipient="admin@example.com",
        subject="Test Alert",
        message="Test alert message",
        status=AlertStatus.PENDING.value,
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    
    assert alert.id is not None
    assert alert.channel == NotificationChannel.EMAIL.value
    assert alert.status == AlertStatus.PENDING.value
    assert alert.acknowledged is False


def test_rule_model(db_session):
    """Test Rule model creation."""
    rule = Rule(
        name="Missing Helmet Detection",
        description="Detect missing helmet violations",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        is_active=True,
        confidence_threshold=0.7,
        conditions={"class": "person", "required_ppe": ["helmet"]},
    )
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    
    assert rule.id is not None
    assert rule.name == "Missing Helmet Detection"
    assert rule.event_code == "missing_helmet"
    assert rule.is_active is True
    assert rule.confidence_threshold == 0.7


def test_audit_log_model(db_session):
    """Test AuditLog model creation."""
    audit_log = AuditLog(
        action="user.login",
        resource_type="user",
        ip_address="192.168.1.1",
        status="success",
    )
    db_session.add(audit_log)
    db_session.commit()
    db_session.refresh(audit_log)
    
    assert audit_log.id is not None
    assert audit_log.action == "user.login"
    assert audit_log.status == "success"

