"""
Unit tests for authentication API endpoints.
"""
import sys
from pathlib import Path
import pytest
from fastapi import status

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models.db.user import User
from app.core.security import get_password_hash
from models.enums import UserRole


def test_register_endpoint(client, db_session):
    """Test user registration endpoint."""
    user_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "TestPassword123!",
        "full_name": "New User",
        "role": UserRole.VIEWER,
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "password" not in data  # Password should not be in response


def test_register_duplicate_email(client, db_session):
    """Test registration with duplicate email."""
    user_data = {
        "email": "duplicate@example.com",
        "username": "user1",
        "password": "TestPassword123!",
    }
    
    # Create first user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to create duplicate
    user_data["username"] = "user2"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_register_duplicate_username(client, db_session):
    """Test registration with duplicate username."""
    user_data = {
        "email": "user1@example.com",
        "username": "duplicate",
        "password": "TestPassword123!",
    }
    
    # Create first user
    client.post("/api/v1/auth/register", json=user_data)
    
    # Try to create duplicate
    user_data["email"] = "user2@example.com"
    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_login_endpoint(client, db_session):
    """Test login endpoint."""
    # Create a user first
    user = User(
        email="login@example.com",
        username="loginuser",
        hashed_password=get_password_hash("TestPassword123!"),
        role=UserRole.VIEWER.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    # Test login
    login_data = {
        "username": "loginuser",
        "password": "TestPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0


def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials."""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user(client, db_session):
    """Test login with inactive user."""
    user = User(
        email="inactive@example.com",
        username="inactive",
        hashed_password=get_password_hash("TestPassword123!"),
        role=UserRole.VIEWER.value,
        is_active=False,  # Inactive
    )
    db_session.add(user)
    db_session.commit()
    
    login_data = {
        "username": "inactive",
        "password": "TestPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_login_with_email(client, db_session):
    """Test login using email instead of username."""
    user = User(
        email="email@example.com",
        username="emailuser",
        hashed_password=get_password_hash("TestPassword123!"),
        role=UserRole.VIEWER.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    
    login_data = {
        "username": "email@example.com",  # Using email
        "password": "TestPassword123!",
    }
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

