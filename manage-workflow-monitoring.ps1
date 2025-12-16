# Management script for Workflow Monitoring Platform
# Manages frontend and backend servers

$PROJECT_NAME = "workflow-monitoring"
$FRONTEND_DIR = Join-Path $PSScriptRoot "frontend"
$BACKEND_DIR = Join-Path $PSScriptRoot "backend"
$FRONTEND_PORT = 3009
$BACKEND_PORT = 8000
$PID_FILE = Join-Path $PSScriptRoot ".server_pids.json"

function Load-Pids {
    if (Test-Path $PID_FILE) {
        try {
            return Get-Content $PID_FILE | ConvertFrom-Json
        } catch {
            return @{}
        }
    }
    return @{}
}

function Save-Pids {
    param([hashtable]$Pids)
    $Pids | ConvertTo-Json | Set-Content $PID_FILE
}

function Test-ProcessRunning {
    param([int]$Pid)
    try {
        $process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        return $null -ne $process
    } catch {
        return $false
    }
}

function Stop-ProcessById {
    param([int]$Pid)
    try {
        $process = Get-Process -Id $Pid -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $Pid -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Write-Warning "Error stopping process $Pid : $_"
    }
}

function Start-Backend {
    Write-Host "[$PROJECT_NAME] Starting backend server on port $BACKEND_PORT..." -ForegroundColor Green
    
    $venvPython = Join-Path $BACKEND_DIR "venv\Scripts\python.exe"
    
    if (-not (Test-Path $venvPython)) {
        Write-Host "[$PROJECT_NAME] Virtual environment not found. Please create it first:" -ForegroundColor Yellow
        Write-Host "  cd backend && python -m venv venv" -ForegroundColor Yellow
        return $null
    }
    
    Push-Location $BACKEND_DIR
    try {
        $process = Start-Process -FilePath $venvPython -ArgumentList @(
            "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", $BACKEND_PORT,
            "--reload"
        ) -PassThru -WindowStyle Hidden
        
        Start-Sleep -Seconds 2
        return $process.Id
    } finally {
        Pop-Location
    }
}

function Start-Frontend {
    Write-Host "[$PROJECT_NAME] Starting frontend server on port $FRONTEND_PORT..." -ForegroundColor Green
    
    if (-not (Test-Path (Join-Path $FRONTEND_DIR "node_modules"))) {
        Write-Host "[$PROJECT_NAME] node_modules not found. Installing dependencies..." -ForegroundColor Yellow
        Push-Location $FRONTEND_DIR
        npm install
        Pop-Location
    }
    
    Push-Location $FRONTEND_DIR
    try {
        $process = Start-Process -FilePath "npm" -ArgumentList @("run", "dev") -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 2
        return $process.Id
    } finally {
        Pop-Location
    }
}

function Start-Servers {
    $pids = Load-Pids
    
    # Check if backend is already running
    if ($pids.backend -and (Test-ProcessRunning -Pid $pids.backend)) {
        Write-Host "[$PROJECT_NAME] Backend is already running (PID: $($pids.backend))" -ForegroundColor Yellow
    } else {
        $backendPid = Start-Backend
        if ($backendPid) {
            $pids.backend = $backendPid
            Write-Host "[$PROJECT_NAME] Backend started with PID: $backendPid" -ForegroundColor Green
        }
    }
    
    Start-Sleep -Seconds 2
    
    # Check if frontend is already running
    if ($pids.frontend -and (Test-ProcessRunning -Pid $pids.frontend)) {
        Write-Host "[$PROJECT_NAME] Frontend is already running (PID: $($pids.frontend))" -ForegroundColor Yellow
    } else {
        $frontendPid = Start-Frontend
        if ($frontendPid) {
            $pids.frontend = $frontendPid
            Write-Host "[$PROJECT_NAME] Frontend started with PID: $frontendPid" -ForegroundColor Green
        }
    }
    
    Save-Pids -Pids $pids
    Write-Host ""
    Write-Host "[$PROJECT_NAME] Servers started!" -ForegroundColor Green
    Write-Host "  Backend:  http://localhost:$BACKEND_PORT" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:$FRONTEND_PORT" -ForegroundColor Cyan
}

function Stop-Servers {
    $pids = Load-Pids
    
    if ($pids.backend) {
        if (Test-ProcessRunning -Pid $pids.backend) {
            Write-Host "[$PROJECT_NAME] Stopping backend (PID: $($pids.backend))..." -ForegroundColor Yellow
            Stop-ProcessById -Pid $pids.backend
        } else {
            Write-Host "[$PROJECT_NAME] Backend is not running" -ForegroundColor Yellow
        }
        $pids.backend = $null
    }
    
    if ($pids.frontend) {
        if (Test-ProcessRunning -Pid $pids.frontend) {
            Write-Host "[$PROJECT_NAME] Stopping frontend (PID: $($pids.frontend))..." -ForegroundColor Yellow
            Stop-ProcessById -Pid $pids.frontend
        } else {
            Write-Host "[$PROJECT_NAME] Frontend is not running" -ForegroundColor Yellow
        }
        $pids.frontend = $null
    }
    
    Save-Pids -Pids $pids
    Write-Host "[$PROJECT_NAME] Servers stopped!" -ForegroundColor Green
}

function Restart-Servers {
    Write-Host "[$PROJECT_NAME] Restarting servers..." -ForegroundColor Yellow
    Stop-Servers
    Start-Sleep -Seconds 2
    Start-Servers
}

function Get-ServerStatus {
    $pids = Load-Pids
    
    Write-Host ""
    Write-Host "[$PROJECT_NAME] Server Status:" -ForegroundColor Cyan
    Write-Host ("=" * 50) -ForegroundColor Gray
    
    # Backend status
    if ($pids.backend) {
        if (Test-ProcessRunning -Pid $pids.backend) {
            Write-Host "✓ Backend:  Running (PID: $($pids.backend))" -ForegroundColor Green
            Write-Host "  URL:      http://localhost:$BACKEND_PORT" -ForegroundColor Gray
        } else {
            Write-Host "✗ Backend:  Not running (stale PID: $($pids.backend))" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Backend:  Not running" -ForegroundColor Red
    }
    
    # Frontend status
    if ($pids.frontend) {
        if (Test-ProcessRunning -Pid $pids.frontend) {
            Write-Host "✓ Frontend: Running (PID: $($pids.frontend))" -ForegroundColor Green
            Write-Host "  URL:      http://localhost:$FRONTEND_PORT" -ForegroundColor Gray
        } else {
            Write-Host "✗ Frontend: Not running (stale PID: $($pids.frontend))" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Frontend: Not running" -ForegroundColor Red
    }
    
    Write-Host ("=" * 50) -ForegroundColor Gray
}

# Main script logic
if ($args.Count -eq 0) {
    Write-Host "Usage: .\manage-workflow-monitoring.ps1 {start|stop|restart|status}" -ForegroundColor Yellow
    exit 1
}

$command = $args[0].ToLower()

switch ($command) {
    "start" {
        Start-Servers
    }
    "stop" {
        Stop-Servers
    }
    "restart" {
        Restart-Servers
    }
    "status" {
        Get-ServerStatus
    }
    default {
        Write-Host "Unknown command: $command" -ForegroundColor Red
        Write-Host "Usage: .\manage-workflow-monitoring.ps1 {start|stop|restart|status}" -ForegroundColor Yellow
        exit 1
    }
}

