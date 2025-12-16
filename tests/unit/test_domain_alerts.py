"""
Unit tests for alert domain service and repository.
"""
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from models.schemas.alert import AlertCreate
from models.enums import AlertStatus, NotificationChannel
from domain.alerts.repository import AlertRepository
from domain.alerts.service import AlertService


def test_alert_repository_create(db_session: Session):
    """Test alert repository create."""
    repo = AlertRepository(db_session)
    alert_data = AlertCreate(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        subject="Test Alert",
        message="Test message",
    )
    alert = repo.create(alert_data)
    
    assert alert.id is not None
    assert alert.channel == NotificationChannel.EMAIL.value
    assert alert.status == AlertStatus.PENDING.value


def test_alert_repository_update_status(db_session: Session):
    """Test alert repository update status."""
    repo = AlertRepository(db_session)
    alert_data = AlertCreate(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
    )
    alert = repo.create(alert_data)
    
    updated = repo.update_status(alert.id, AlertStatus.SENT)
    assert updated is not None
    assert updated.status == AlertStatus.SENT.value


def test_alert_service_create(db_session: Session):
    """Test alert service create."""
    service = AlertService(db_session)
    alert_data = AlertCreate(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        subject="Test Alert",
    )
    alert = service.create_alert(alert_data)
    
    assert alert.id is not None
    assert alert.channel == NotificationChannel.EMAIL.value


def test_alert_service_mark_sent(db_session: Session):
    """Test alert service mark as sent."""
    service = AlertService(db_session)
    alert_data = AlertCreate(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
    )
    alert = service.create_alert(alert_data)
    
    sent = service.mark_sent(alert.id)
    assert sent is not None
    assert sent.status == AlertStatus.SENT.value


def test_alert_service_acknowledge(db_session: Session):
    """Test alert service acknowledge."""
    service = AlertService(db_session)
    alert_data = AlertCreate(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
    )
    alert = service.create_alert(alert_data)
    
    acknowledged = service.acknowledge_alert(alert.id, user_id=1)
    assert acknowledged is not None
    assert acknowledged.acknowledged is True

