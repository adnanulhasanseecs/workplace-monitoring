"""
Unit tests for event domain service and repository.
"""
import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from models.schemas.event import EventCreate, EventFilter
from models.enums import EventType, EventSeverity
from domain.events.repository import EventRepository
from domain.events.service import EventService
from domain.cameras.repository import CameraRepository
from models.schemas.camera import CameraCreate


def test_event_repository_create(db_session: Session):
    """Test event repository create."""
    # Create camera first
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    repo = EventRepository(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    event = repo.create(event_data)
    
    assert event.id is not None
    assert event.camera_id == camera.id
    assert event.event_code == "missing_helmet"
    assert event.acknowledged is False


def test_event_repository_get_by_id(db_session: Session):
    """Test event repository get by ID."""
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    repo = EventRepository(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    event = repo.create(event_data)
    
    found = repo.get_by_id(event.id)
    assert found is not None
    assert found.id == event.id


def test_event_repository_acknowledge(db_session: Session):
    """Test event repository acknowledge."""
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    repo = EventRepository(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    event = repo.create(event_data)
    
    acknowledged = repo.acknowledge(event.id, user_id=1)
    assert acknowledged is not None
    assert acknowledged.acknowledged is True
    assert acknowledged.acknowledged_by == 1


def test_event_service_create(db_session: Session):
    """Test event service create."""
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    service = EventService(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    event = service.create_event(event_data)
    
    assert event.id is not None
    assert event.camera_id == camera.id


def test_event_service_list_events(db_session: Session):
    """Test event service list events."""
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    service = EventService(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    service.create_event(event_data)
    
    filters = EventFilter(camera_id=camera.id, limit=10)
    events = service.list_events(filters)
    assert len(events) >= 1


def test_event_service_acknowledge(db_session: Session):
    """Test event service acknowledge."""
    camera_repo = CameraRepository(db_session)
    camera = camera_repo.create(CameraCreate(name="Test Camera", stream_type="rtsp"))
    
    service = EventService(db_session)
    event_data = EventCreate(
        camera_id=camera.id,
        event_type=EventType.PPE_VIOLATION.value,
        event_code="missing_helmet",
        severity=EventSeverity.HIGH,
        confidence=0.95,
        timestamp=datetime.utcnow(),
    )
    event = service.create_event(event_data)
    
    acknowledged = service.acknowledge_event(event.id, user_id=1)
    assert acknowledged is not None
    assert acknowledged.acknowledged is True

