# Testing Guide - Workflow Monitoring Platform

## Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **Node.js 18+** installed
3. **PostgreSQL** (optional, SQLite used by default)
4. **Redis** (optional for basic testing, required for job queue)

### Step 1: Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
# Copy .env.example to .env and configure if needed
```

### Step 2: Frontend Setup

```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Frontend will run on http://localhost:3009
```

### Step 3: Start Services

**Option A: Using Management Script (Recommended)**

```powershell
# From project root
.\manage-workflow-monitoring.ps1 start
```

**Option B: Manual Start**

**Backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```powershell
cd frontend
npm run dev
```

### Step 4: Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3009

## Testing the API

### 1. Create Admin User

```powershell
# Using PowerShell
$body = @{
    email = "admin@example.com"
    username = "admin"
    password = "Admin123!"
    full_name = "Admin User"
    role = "admin"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

### 2. Login and Get Token

```powershell
$loginBody = @{
    username = "admin"
    password = "Admin123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $loginBody

$token = $response.access_token
Write-Host "Token: $token"
```

### 3. Test Camera API

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

# Create a camera
$cameraBody = @{
    name = "Test Camera 1"
    stream_type = "rtsp"
    stream_url = "rtsp://example.com/stream"
    location = "Building A"
} | ConvertTo-Json

$camera = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/cameras" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $cameraBody

Write-Host "Created Camera: $($camera | ConvertTo-Json)"

# List cameras
$cameras = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/cameras" `
    -Method GET `
    -Headers $headers

Write-Host "Cameras: $($cameras | ConvertTo-Json)"
```

### 4. Test Rules API

```powershell
$ruleBody = @{
    name = "Missing Helmet Detection"
    event_code = "missing_helmet"
    event_type = "ppe_violation"
    confidence_threshold = 0.75
    conditions = @{
        class = "person"
        required_ppe = @("helmet")
    }
} | ConvertTo-Json

$rule = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/rules" `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $ruleBody

Write-Host "Created Rule: $($rule | ConvertTo-Json)"
```

## Using Swagger UI (Easiest Method)

1. Open http://localhost:8000/docs in your browser
2. Click "Authorize" button
3. Login using `/api/v1/auth/login` endpoint first
4. Copy the `access_token` from response
5. Click "Authorize" again and paste: `Bearer <your_token>`
6. Now you can test all endpoints directly from the UI

## Testing Video Ingestion

### Test File Upload

```powershell
# Note: This requires a video file
$filePath = "C:\path\to\your\video.mp4"

$formData = @{
    file = Get-Item $filePath
    camera_id = 1
} | ConvertTo-Json

# This endpoint needs to be implemented in Phase 3 ingestion API
```

## Running Tests

```powershell
# Run all tests
cd backend
.\venv\Scripts\Activate.ps1
pytest ..\tests\ -v

# Run specific test suite
pytest ..\tests\unit\ -v
pytest ..\tests\integration\ -v

# Run with coverage
pytest ..\tests\ --cov=app --cov=domain --cov=worker --cov-report=html
```

## Current Implementation Status

### ✅ Ready for Testing

- **Authentication**: Login, Register, JWT tokens
- **Camera Management**: CRUD operations
- **Event Queries**: List, filter, acknowledge events
- **Alert Management**: List, acknowledge alerts
- **Rule Configuration**: CRUD operations for rules
- **API Documentation**: Swagger UI at `/docs`

### ⚠️ Requires Additional Setup

- **Database**: SQLite used by default (no setup needed), PostgreSQL optional
- **Redis**: Required for job queue (optional for basic API testing)
- **GPU/CUDA**: Required for video processing (optional for API testing)

### 🚧 Not Yet Implemented

- Video upload API endpoint (ingestion service ready, API endpoint pending)
- Real-time video processing (worker ready, needs queue integration)
- Frontend dashboard (basic React app, needs UI components)
- Event detection pipeline (rules engine pending)

## Troubleshooting

### Backend won't start

1. Check if port 8000 is available
2. Verify virtual environment is activated
3. Check dependencies: `pip install -r requirements.txt`
4. Check database: SQLite file should be created automatically

### Frontend won't start

1. Check if port 3009 is available
2. Verify Node.js version: `node --version` (should be 18+)
3. Reinstall dependencies: `npm install`
4. Check for port conflicts

### Authentication fails

1. Make sure you've registered a user first
2. Check JWT_SECRET_KEY in environment (defaults provided)
3. Verify token format: `Bearer <token>`

### Database errors

1. SQLite database is created automatically at `backend/app.db`
2. For PostgreSQL, set `DATABASE_URL` in `.env`
3. Run migrations: `alembic upgrade head` (if using Alembic)

## Next Steps for Full Testing

1. **Add Video Upload Endpoint**: Connect ingestion service to API
2. **Implement Worker Queue Integration**: Connect worker to Redis queue
3. **Add Frontend Components**: Build dashboard UI
4. **Implement Rules Engine**: Connect detection to rules evaluation

## API Endpoints Available

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get token

### Cameras
- `GET /api/v1/cameras` - List cameras
- `POST /api/v1/cameras` - Create camera
- `GET /api/v1/cameras/{id}` - Get camera
- `PUT /api/v1/cameras/{id}` - Update camera
- `DELETE /api/v1/cameras/{id}` - Delete camera
- `POST /api/v1/cameras/{id}/activate` - Activate camera
- `POST /api/v1/cameras/{id}/deactivate` - Deactivate camera

### Events
- `GET /api/v1/events` - List events (with filters)
- `GET /api/v1/events/{id}` - Get event
- `POST /api/v1/events/{id}/acknowledge` - Acknowledge event
- `GET /api/v1/events/cameras/{camera_id}` - Get camera events
- `GET /api/v1/events/unacknowledged/recent` - Get recent unacknowledged

### Alerts
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{id}` - Get alert
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert
- `GET /api/v1/alerts/pending/list` - Get pending alerts

### Rules
- `GET /api/v1/rules` - List rules
- `POST /api/v1/rules` - Create rule
- `GET /api/v1/rules/{id}` - Get rule
- `PUT /api/v1/rules/{id}` - Update rule
- `DELETE /api/v1/rules/{id}` - Delete rule
- `POST /api/v1/rules/{id}/activate` - Activate rule
- `POST /api/v1/rules/{id}/deactivate` - Deactivate rule

