#!/usr/bin/env python3
"""
Management script for Workflow Monitoring Platform.
Manages frontend and backend servers.
"""
import os
import sys
import subprocess
import signal
import time
import json
from pathlib import Path
from typing import Optional

PROJECT_NAME = "workflow-monitoring"
FRONTEND_DIR = Path(__file__).parent / "frontend"
BACKEND_DIR = Path(__file__).parent / "backend"
FRONTEND_PORT = 3009
BACKEND_PORT = 8000
PID_FILE = Path(__file__).parent / ".server_pids.json"


def load_pids() -> dict:
    """Load process IDs from file."""
    if PID_FILE.exists():
        try:
            with open(PID_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_pids(pids: dict):
    """Save process IDs to file."""
    with open(PID_FILE, "w") as f:
        json.dump(pids, f)


def is_process_running(pid: int) -> bool:
    """Check if a process is running."""
    try:
        if sys.platform == "win32":
            # Windows
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
            )
            return str(pid) in result.stdout
        else:
            # Unix-like
            os.kill(pid, 0)
            return True
    except (OSError, subprocess.SubprocessError):
        return False


def kill_process(pid: int):
    """Kill a process."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], check=False)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            if is_process_running(pid):
                os.kill(pid, signal.SIGKILL)
    except Exception as e:
        print(f"Error killing process {pid}: {e}")


def start_backend():
    """Start the FastAPI backend server."""
    print(f"[{PROJECT_NAME}] Starting backend server on port {BACKEND_PORT}...")
    
    os.chdir(BACKEND_DIR)
    
    # Check if virtual environment exists
    venv_python = None
    if sys.platform == "win32":
        venv_python = BACKEND_DIR / "venv" / "Scripts" / "python.exe"
    else:
        venv_python = BACKEND_DIR / "venv" / "bin" / "python"
    
    if not venv_python.exists():
        print(f"[{PROJECT_NAME}] Virtual environment not found. Please create it first:")
        print(f"  cd backend && python -m venv venv")
        return None
    
    # Start uvicorn
    if sys.platform == "win32":
        process = subprocess.Popen(
            [
                str(venv_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                str(BACKEND_PORT),
                "--reload",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
        )
    else:
        process = subprocess.Popen(
            [
                str(venv_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                str(BACKEND_PORT),
                "--reload",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    
    os.chdir(Path(__file__).parent)
    return process.pid


def start_frontend():
    """Start the React frontend server."""
    print(f"[{PROJECT_NAME}] Starting frontend server on port {FRONTEND_PORT}...")
    
    os.chdir(FRONTEND_DIR)
    
    # Check if node_modules exists
    if not (FRONTEND_DIR / "node_modules").exists():
        print(f"[{PROJECT_NAME}] node_modules not found. Installing dependencies...")
        subprocess.run(["npm", "install"], check=False)
    
    # Start Vite dev server
    if sys.platform == "win32":
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    else:
        process = subprocess.Popen(
            ["npm", "run", "dev"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    
    os.chdir(Path(__file__).parent)
    return process.pid


def start():
    """Start both servers."""
    pids = load_pids()
    
    # Check if already running
    if pids.get("backend") and is_process_running(pids["backend"]):
        print(f"[{PROJECT_NAME}] Backend is already running (PID: {pids['backend']})")
    else:
        backend_pid = start_backend()
        if backend_pid:
            pids["backend"] = backend_pid
            print(f"[{PROJECT_NAME}] Backend started with PID: {backend_pid}")
    
    time.sleep(2)  # Give backend time to start
    
    if pids.get("frontend") and is_process_running(pids["frontend"]):
        print(f"[{PROJECT_NAME}] Frontend is already running (PID: {pids['frontend']})")
    else:
        frontend_pid = start_frontend()
        if frontend_pid:
            pids["frontend"] = frontend_pid
            print(f"[{PROJECT_NAME}] Frontend started with PID: {frontend_pid}")
    
    save_pids(pids)
    print(f"\n[{PROJECT_NAME}] Servers started!")
    print(f"  Backend: http://localhost:{BACKEND_PORT}")
    print(f"  Frontend: http://localhost:{FRONTEND_PORT}")


def stop():
    """Stop both servers."""
    pids = load_pids()
    
    if pids.get("backend"):
        if is_process_running(pids["backend"]):
            print(f"[{PROJECT_NAME}] Stopping backend (PID: {pids['backend']})...")
            kill_process(pids["backend"])
        else:
            print(f"[{PROJECT_NAME}] Backend is not running")
        pids["backend"] = None
    
    if pids.get("frontend"):
        if is_process_running(pids["frontend"]):
            print(f"[{PROJECT_NAME}] Stopping frontend (PID: {pids['frontend']})...")
            kill_process(pids["frontend"])
        else:
            print(f"[{PROJECT_NAME}] Frontend is not running")
        pids["frontend"] = None
    
    save_pids(pids)
    print(f"[{PROJECT_NAME}] Servers stopped!")


def restart():
    """Restart both servers."""
    print(f"[{PROJECT_NAME}] Restarting servers...")
    stop()
    time.sleep(2)
    start()


def status():
    """Check status of both servers."""
    pids = load_pids()
    
    print(f"\n[{PROJECT_NAME}] Server Status:")
    print("=" * 50)
    
    # Backend status
    if pids.get("backend"):
        if is_process_running(pids["backend"]):
            print(f"✓ Backend: Running (PID: {pids['backend']})")
            print(f"  URL: http://localhost:{BACKEND_PORT}")
        else:
            print(f"✗ Backend: Not running (stale PID: {pids['backend']})")
    else:
        print("✗ Backend: Not running")
    
    # Frontend status
    if pids.get("frontend"):
        if is_process_running(pids["frontend"]):
            print(f"✓ Frontend: Running (PID: {pids['frontend']})")
            print(f"  URL: http://localhost:{FRONTEND_PORT}")
        else:
            print(f"✗ Frontend: Not running (stale PID: {pids['frontend']})")
    else:
        print("✗ Frontend: Not running")
    
    print("=" * 50)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} {{start|stop|restart|status}}")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "start":
        start()
    elif command == "stop":
        stop()
    elif command == "restart":
        restart()
    elif command == "status":
        status()
    else:
        print(f"Unknown command: {command}")
        print(f"Usage: python {sys.argv[0]} {{start|stop|restart|status}}")
        sys.exit(1)


if __name__ == "__main__":
    main()

