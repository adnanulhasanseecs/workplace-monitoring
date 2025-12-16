"""
Alert management API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from gateway.middleware.auth import get_current_user
from models.db.user import User
from models.enums import AlertStatus, NotificationChannel
from models.schemas.alert import AlertResponse
from domain.alerts.service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0, description="Number of alerts to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts to return"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    channel: Optional[NotificationChannel] = Query(None, description="Filter by notification channel"),
    event_id: Optional[int] = Query(None, description="Filter by event ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List alerts with optional filters.
    Requires: Any authenticated user.
    """
    service = AlertService(db)
    return service.list_alerts(
        skip=skip,
        limit=limit,
        status=status,
        channel=channel,
        event_id=event_id,
    )


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get alert by ID.
    Requires: Any authenticated user.
    """
    service = AlertService(db)
    alert = service.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Acknowledge an alert.
    Requires: Any authenticated user.
    """
    service = AlertService(db)
    alert = service.acknowledge_alert(alert_id, current_user.id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.get("/pending/list", response_model=List[AlertResponse])
def get_pending_alerts(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of alerts to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get pending alerts.
    Requires: Any authenticated user.
    """
    service = AlertService(db)
    return service.get_pending_alerts(limit)


@router.get("/stats/count")
def get_alert_count(
    status: Optional[AlertStatus] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get alert count.
    Requires: Any authenticated user.
    """
    service = AlertService(db)
    return {"count": service.get_alert_count(status=status)}

