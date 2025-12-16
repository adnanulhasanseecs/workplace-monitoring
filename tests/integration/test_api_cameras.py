"""
Integration tests for camera API endpoints.
"""
import sys
from pathlib import Path
import pytest

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import get_password_hash
from models.db.user import User
from models.enums import UserRole

client = TestClient(app)


@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(test_user):
    """Get auth token for test user."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "TestPassword123!"},
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


def test_create_camera(auth_token):
    """Test create camera endpoint."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.post(
        "/api/v1/cameras",
        json={
            "name": "Test Camera",
            "stream_type": "rtsp",
            "stream_url": "rtsp://example.com/stream",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Camera"
    assert "id" in data


def test_list_cameras(auth_token):
    """Test list cameras endpoint."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/v1/cameras", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_camera(auth_token):
    """Test get camera endpoint."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create camera first
    create_response = client.post(
        "/api/v1/cameras",
        json={"name": "Test Camera", "stream_type": "rtsp"},
        headers=headers,
    )
    camera_id = create_response.json()["id"]
    
    # Get camera
    response = client.get(f"/api/v1/cameras/{camera_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == camera_id


def test_update_camera(auth_token):
    """Test update camera endpoint."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create camera first
    create_response = client.post(
        "/api/v1/cameras",
        json={"name": "Test Camera", "stream_type": "rtsp"},
        headers=headers,
    )
    camera_id = create_response.json()["id"]
    
    # Update camera
    response = client.put(
        f"/api/v1/cameras/{camera_id}",
        json={"name": "Updated Camera"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Camera"


def test_delete_camera(auth_token):
    """Test delete camera endpoint."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create camera first
    create_response = client.post(
        "/api/v1/cameras",
        json={"name": "Test Camera", "stream_type": "rtsp"},
        headers=headers,
    )
    camera_id = create_response.json()["id"]
    
    # Delete camera
    response = client.delete(f"/api/v1/cameras/{camera_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify deleted
    get_response = client.get(f"/api/v1/cameras/{camera_id}", headers=headers)
    assert get_response.status_code == 404

