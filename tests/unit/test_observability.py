"""
Unit tests for observability components.
"""
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from observability.logging import setup_logging, get_logger
from observability.metrics import (
    http_requests_total,
    http_request_duration,
    events_detected_total,
)


def test_logging_setup():
    """Test logging setup."""
    setup_logging()
    logger = get_logger(__name__)
    assert logger is not None


def test_logger_functionality():
    """Test logger functionality."""
    setup_logging()
    logger = get_logger("test_logger")
    
    # Should not raise exception
    logger.info("test_message", key="value")
    logger.warning("test_warning")
    logger.error("test_error")


def test_metrics_initialization():
    """Test metrics initialization."""
    # Metrics should be initialized
    assert http_requests_total is not None
    assert http_request_duration is not None
    assert events_detected_total is not None


def test_metrics_increment():
    """Test metrics increment."""
    # Should not raise exception
    http_requests_total.labels(method="GET", endpoint="/test", status_code=200).inc()
    events_detected_total.labels(event_type="ppe_violation", severity="high").inc()

