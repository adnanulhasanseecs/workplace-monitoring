# Test runner script for Workflow Monitoring Platform
# This script sets up the test environment and runs unit tests

Write-Host "Setting up test environment..." -ForegroundColor Green

# Check if virtual environment exists
$venvPath = "backend\venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv $venvPath
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& "$venvPath\Scripts\Activate.ps1"

# Install test dependencies
Write-Host "Installing test dependencies..." -ForegroundColor Green
pip install -q pytest pytest-asyncio httpx fastapi[all] sqlalchemy pydantic pydantic-settings

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Green
cd backend
pip install -q -r requirements.txt
cd ..

# Set environment variables for testing
$env:SECRET_KEY = "test-secret-key-for-testing-only"
$env:JWT_SECRET_KEY = "test-jwt-secret-key-for-testing-only"
$env:DATABASE_URL = "sqlite:///./test.db"

# Run tests
Write-Host "`nRunning unit tests..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

python -m pytest tests/unit/ -v --tb=short --color=yes

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host "`nAll tests passed!" -ForegroundColor Green
} else {
    Write-Host "`nSome tests failed. Exit code: $exitCode" -ForegroundColor Red
}

exit $exitCode

