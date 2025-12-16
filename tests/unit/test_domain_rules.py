"""
Unit tests for rule domain service and repository.
"""
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from models.schemas.rule import RuleCreate, RuleUpdate
from models.enums import EventType
from domain.rules.repository import RuleRepository
from domain.rules.service import RuleService


def test_rule_repository_create(db_session: Session):
    """Test rule repository create."""
    repo = RuleRepository(db_session)
    rule_data = RuleCreate(
        name="Test Rule",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        conditions={"class": "person", "required_ppe": ["helmet"]},
    )
    rule = repo.create(rule_data)
    
    assert rule.id is not None
    assert rule.name == "Test Rule"
    assert rule.is_active is True


def test_rule_repository_get_active_rules(db_session: Session):
    """Test rule repository get active rules."""
    repo = RuleRepository(db_session)
    rule_data = RuleCreate(
        name="Test Rule",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        conditions={"class": "person"},
    )
    repo.create(rule_data)
    
    active_rules = repo.get_active_rules()
    assert len(active_rules) >= 1


def test_rule_service_create(db_session: Session):
    """Test rule service create."""
    service = RuleService(db_session)
    rule_data = RuleCreate(
        name="Test Rule",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        conditions={"class": "person"},
    )
    rule = service.create_rule(rule_data)
    
    assert rule.id is not None
    assert rule.name == "Test Rule"


def test_rule_service_create_duplicate_name(db_session: Session):
    """Test rule service create with duplicate name."""
    service = RuleService(db_session)
    rule_data = RuleCreate(
        name="Test Rule",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        conditions={"class": "person"},
    )
    service.create_rule(rule_data)
    
    with pytest.raises(ValueError, match="already exists"):
        service.create_rule(rule_data)


def test_rule_service_activate(db_session: Session):
    """Test rule service activate."""
    service = RuleService(db_session)
    rule_data = RuleCreate(
        name="Test Rule",
        event_code="missing_helmet",
        event_type=EventType.PPE_VIOLATION.value,
        conditions={"class": "person"},
        is_active=False,
    )
    rule = service.create_rule(rule_data)
    
    activated = service.activate_rule(rule.id)
    assert activated is not None
    assert activated.is_active is True

