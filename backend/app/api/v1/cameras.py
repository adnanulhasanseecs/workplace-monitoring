"""
Camera management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from gateway.middleware.auth import get_current_user
from gateway.middleware.rbac import require_role
from models.db.user import User
from models.enums import UserRole, CameraStatus
from models.schemas.camera import CameraCreate, CameraUpdate, CameraResponse
from domain.cameras.service import CameraService

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera_data: CameraCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new camera.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = CameraService(db)
    try:
        return service.create_camera(camera_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[CameraResponse])
def list_cameras(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CameraStatus] = None,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List cameras with optional filters.
    Requires: Any authenticated user.
    """
    service = CameraService(db)
    return service.list_cameras(skip=skip, limit=limit, status=status, location=location)


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get camera by ID.
    Requires: Any authenticated user.
    """
    service = CameraService(db)
    camera = service.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.put("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update camera.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = CameraService(db)
    try:
        camera = service.update_camera(camera_id, camera_data)
        if not camera:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
        return camera
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete camera.
    Requires: Admin role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    service = CameraService(db)
    success = service.delete_camera(camera_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")


@router.post("/{camera_id}/activate", response_model=CameraResponse)
def activate_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activate a camera.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = CameraService(db)
    camera = service.activate_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.post("/{camera_id}/deactivate", response_model=CameraResponse)
def deactivate_camera(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivate a camera.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = CameraService(db)
    camera = service.deactivate_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Camera not found")
    return camera


@router.get("/stats/count")
def get_camera_count(
    status: Optional[CameraStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get camera count.
    Requires: Any authenticated user.
    """
    service = CameraService(db)
    return {"count": service.get_camera_count(status=status)}

