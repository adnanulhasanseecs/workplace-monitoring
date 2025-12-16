"""
Unit tests for camera domain service and repository.
"""
import sys
from pathlib import Path
import pytest
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from models.schemas.camera import CameraCreate, CameraUpdate
from models.enums import CameraStatus
from domain.cameras.repository import CameraRepository
from domain.cameras.service import CameraService


def test_camera_repository_create(db_session: Session):
    """Test camera repository create."""
    repo = CameraRepository(db_session)
    camera_data = CameraCreate(
        name="Test Camera",
        stream_type="rtsp",
        stream_url="rtsp://example.com/stream",
    )
    camera = repo.create(camera_data)
    
    assert camera.id is not None
    assert camera.name == "Test Camera"
    assert camera.stream_type == "rtsp"
    assert camera.status == CameraStatus.INACTIVE.value


def test_camera_repository_get_by_id(db_session: Session):
    """Test camera repository get by ID."""
    repo = CameraRepository(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = repo.create(camera_data)
    
    found = repo.get_by_id(camera.id)
    assert found is not None
    assert found.id == camera.id
    assert found.name == "Test Camera"


def test_camera_repository_update(db_session: Session):
    """Test camera repository update."""
    repo = CameraRepository(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = repo.create(camera_data)
    
    update_data = CameraUpdate(name="Updated Camera", location="Building B")
    updated = repo.update(camera.id, update_data)
    
    assert updated is not None
    assert updated.name == "Updated Camera"
    assert updated.location == "Building B"


def test_camera_repository_delete(db_session: Session):
    """Test camera repository delete."""
    repo = CameraRepository(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = repo.create(camera_data)
    
    success = repo.delete(camera.id)
    assert success is True
    
    found = repo.get_by_id(camera.id)
    assert found is None


def test_camera_service_create(db_session: Session):
    """Test camera service create."""
    service = CameraService(db_session)
    camera_data = CameraCreate(
        name="Test Camera",
        stream_type="rtsp",
        stream_url="rtsp://example.com/stream",
    )
    camera = service.create_camera(camera_data)
    
    assert camera.id is not None
    assert camera.name == "Test Camera"


def test_camera_service_create_duplicate_name(db_session: Session):
    """Test camera service create with duplicate name."""
    service = CameraService(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    service.create_camera(camera_data)
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_camera(camera_data)


def test_camera_service_update(db_session: Session):
    """Test camera service update."""
    service = CameraService(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = service.create_camera(camera_data)
    
    update_data = CameraUpdate(name="Updated Camera")
    updated = service.update_camera(camera.id, update_data)
    
    assert updated is not None
    assert updated.name == "Updated Camera"


def test_camera_service_activate(db_session: Session):
    """Test camera service activate."""
    service = CameraService(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = service.create_camera(camera_data)
    
    activated = service.activate_camera(camera.id)
    assert activated is not None
    assert activated.status == CameraStatus.ACTIVE.value


def test_camera_service_deactivate(db_session: Session):
    """Test camera service deactivate."""
    service = CameraService(db_session)
    camera_data = CameraCreate(name="Test Camera", stream_type="rtsp")
    camera = service.create_camera(camera_data)
    service.activate_camera(camera.id)
    
    deactivated = service.deactivate_camera(camera.id)
    assert deactivated is not None
    assert deactivated.status == CameraStatus.INACTIVE.value

