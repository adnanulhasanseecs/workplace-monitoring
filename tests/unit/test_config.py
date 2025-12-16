"""
Unit tests for configuration.
"""
import sys
from pathlib import Path
import pytest
import os

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.config import Settings


def test_settings_defaults():
    """Test default settings values."""
    # Use minimal required settings
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    settings = Settings()
    
    assert settings.APP_NAME == "Workflow Monitoring Platform"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.CORS_ALLOW_CREDENTIALS is True


def test_settings_yolo_config():
    """Test YOLO11 configuration settings."""
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    settings = Settings()
    
    assert settings.YOLO_MODEL_PATH == "./models/yolo11n.pt"
    assert settings.YOLO_CONFIDENCE_THRESHOLD == 0.25
    assert settings.YOLO_IOU_THRESHOLD == 0.45
    assert settings.BATCH_SIZE == 16
    assert settings.GPU_MEMORY_FRACTION == 0.8


def test_settings_redis_config():
    """Test Redis configuration."""
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    settings = Settings()
    
    assert settings.REDIS_HOST == "localhost"
    assert settings.REDIS_PORT == 6379
    assert settings.REDIS_DB_QUEUE == 0
    assert settings.REDIS_DB_CACHE == 1
    assert settings.REDIS_DB_COORDINATION == 2

