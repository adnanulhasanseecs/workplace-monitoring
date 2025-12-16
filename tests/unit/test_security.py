"""
Unit tests for security utilities.
"""
import sys
from pathlib import Path
import pytest
from datetime import timedelta

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    
    # Hashed password should be different from original
    assert hashed != password
    assert len(hashed) > 0
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    
    # Should fail with wrong password
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation():
    """Test JWT token creation."""
    data = {"sub": "1", "username": "testuser", "role": "admin"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_jwt_token_with_expiry():
    """Test JWT token with custom expiry."""
    data = {"sub": "1", "username": "testuser"}
    expires_delta = timedelta(minutes=15)
    token = create_access_token(data, expires_delta=expires_delta)
    
    assert token is not None
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "1"


def test_jwt_token_decode():
    """Test JWT token decoding."""
    data = {"sub": "123", "username": "testuser", "role": "admin"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["username"] == "testuser"
    assert decoded["role"] == "admin"


def test_jwt_token_decode_invalid():
    """Test JWT token decoding with invalid token."""
    invalid_token = "invalid.token.here"
    decoded = decode_access_token(invalid_token)
    assert decoded is None


def test_jwt_token_expiry():
    """Test JWT token expiry."""
    data = {"sub": "1"}
    expires_delta = timedelta(seconds=-1)  # Already expired
    token = create_access_token(data, expires_delta=expires_delta)
    
    decoded = decode_access_token(token)
    # Should return None for expired token
    assert decoded is None

