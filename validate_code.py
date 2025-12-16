"""
Simple code validation script to check for common issues.
Can be run without pytest to validate code structure.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set test environment
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

errors = []
warnings = []

print("Validating code structure...")
print("=" * 50)

# Test imports
try:
    from app.core.config import Settings, settings
    print("[OK] Configuration module imports successfully")
except Exception as e:
    errors.append(f"Config import failed: {e}")
    print(f"[ERROR] Config import failed: {e}")

try:
    from app.core.security import verify_password, get_password_hash, create_access_token
    print("[OK] Security module imports successfully")
except Exception as e:
    errors.append(f"Security import failed: {e}")
    print(f"[ERROR] Security import failed: {e}")

try:
    from models.db.user import User
    from models.db.camera import Camera
    from models.db.event import Event
    print("[OK] Database models import successfully")
except Exception as e:
    errors.append(f"Models import failed: {e}")
    print(f"[ERROR] Models import failed: {e}")

try:
    from models.schemas.auth import UserCreate, LoginRequest
    from models.schemas.camera import CameraCreate
    print("[OK] Pydantic schemas import successfully")
except Exception as e:
    errors.append(f"Schemas import failed: {e}")
    print(f"[ERROR] Schemas import failed: {e}")

try:
    from models.enums import UserRole, EventType, EventSeverity
    print("[OK] Enums import successfully")
except Exception as e:
    errors.append(f"Enums import failed: {e}")
    print(f"[ERROR] Enums import failed: {e}")

try:
    from observability.logging import setup_logging, get_logger
    print("[OK] Observability module imports successfully")
except Exception as e:
    errors.append(f"Observability import failed: {e}")
    print(f"[ERROR] Observability import failed: {e}")

# Test basic functionality
try:
    from app.core.security import get_password_hash, verify_password
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) == True
    assert verify_password("WrongPassword", hashed) == False
    print("[OK] Password hashing works correctly")
except Exception as e:
    errors.append(f"Password hashing test failed: {e}")
    print(f"[ERROR] Password hashing test failed: {e}")

try:
    from app.core.security import create_access_token, decode_access_token
    data = {"sub": "123", "username": "test"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    print("[OK] JWT token creation and decoding works")
except Exception as e:
    errors.append(f"JWT test failed: {e}")
    print(f"[ERROR] JWT test failed: {e}")

try:
    from models.schemas.auth import UserCreate
    user = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Test123!",
    )
    assert user.email == "test@example.com"
    print("[OK] Pydantic schema validation works")
except Exception as e:
    errors.append(f"Schema validation test failed: {e}")
    print(f"[ERROR] Schema validation test failed: {e}")

print("=" * 50)

if errors:
    print(f"\n[FAILED] Found {len(errors)} error(s):")
    for error in errors:
        print(f"  - {error}")
    sys.exit(1)
else:
    print("\n[SUCCESS] All validations passed!")
    print("\nTo run full unit tests, install pytest and run:")
    print("  cd backend")
    print("  python -m pytest ../tests/unit/ -v")
    sys.exit(0)

