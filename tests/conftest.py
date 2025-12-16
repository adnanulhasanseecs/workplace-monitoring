"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from app.core.database import Base, get_db
    from app.core.config import settings
    from app.main import app
except ImportError:
    # Try alternative import path
    import sys
    import os
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend')
    sys.path.insert(0, backend_dir)
    from app.core.database import Base, get_db
    from app.core.config import settings
    from app.main import app

# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User",
    }

