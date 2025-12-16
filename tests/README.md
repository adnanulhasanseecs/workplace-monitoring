# Testing Guide

## Running Tests

### Prerequisites

1. **Set up virtual environment:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install test dependencies:**
```powershell
pip install pytest pytest-asyncio httpx
```

### Run All Tests

```powershell
# From project root
cd backend
python -m pytest ../tests/unit/ -v
```

### Run Specific Test File

```powershell
python -m pytest ../tests/unit/test_models.py -v
python -m pytest ../tests/unit/test_security.py -v
python -m pytest ../tests/unit/test_auth_api.py -v
```

### Run with Coverage

```powershell
pip install pytest-cov
python -m pytest ../tests/unit/ --cov=app --cov=models --cov-report=html
```

## Test Structure

- `tests/unit/` - Unit tests for individual components
  - `test_models.py` - Database model tests
  - `test_schemas.py` - Pydantic schema validation tests
  - `test_security.py` - Security utilities (JWT, password hashing)
  - `test_auth_api.py` - Authentication API endpoint tests
  - `test_config.py` - Configuration tests
  - `test_observability.py` - Logging and metrics tests

- `tests/integration/` - Integration tests (to be added)
- `tests/e2e/` - End-to-end tests (to be added)

## Test Coverage

Phase 1 tests cover:
- ✅ Database models (User, Camera, Event, Alert, Rule, AuditLog)
- ✅ Pydantic schemas validation
- ✅ JWT token creation and validation
- ✅ Password hashing and verification
- ✅ Authentication endpoints (login, register)
- ✅ Configuration management
- ✅ Observability setup

## Environment Variables for Testing

Tests use SQLite in-memory database. Set these environment variables:

```powershell
$env:SECRET_KEY = "test-secret-key"
$env:JWT_SECRET_KEY = "test-jwt-secret"
$env:DATABASE_URL = "sqlite:///./test.db"
```

