"""
Event querying API endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from gateway.middleware.auth import get_current_user
from models.db.user import User
from models.enums import EventSeverity
from models.schemas.event import EventResponse, EventFilter
from domain.events.service import EventService

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=List[EventResponse])
def list_events(
    camera_id: int = Query(None, description="Filter by camera ID"),
    event_type: str = Query(None, description="Filter by event type"),
    event_code: str = Query(None, description="Filter by event code"),
    severity: EventSeverity = Query(None, description="Filter by severity"),
    start_date: datetime = Query(None, description="Filter by start date"),
    end_date: datetime = Query(None, description="Filter by end date"),
    acknowledged: bool = Query(None, description="Filter by acknowledged status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    offset: int = Query(0, ge=0, description="Number of events to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List events with filters.
    Requires: Any authenticated user.
    """
    filters = EventFilter(
        camera_id=camera_id,
        event_type=event_type,
        event_code=event_code,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        acknowledged=acknowledged,
        limit=limit,
        offset=offset,
    )
    
    service = EventService(db)
    return service.list_events(filters)


@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get event by ID.
    Requires: Any authenticated user.
    """
    service = EventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.post("/{event_id}/acknowledge", response_model=EventResponse)
def acknowledge_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Acknowledge an event.
    Requires: Any authenticated user.
    """
    service = EventService(db)
    event = service.acknowledge_event(event_id, current_user.id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return event


@router.get("/cameras/{camera_id}", response_model=List[EventResponse])
def get_camera_events(
    camera_id: int,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get events for a specific camera.
    Requires: Any authenticated user.
    """
    service = EventService(db)
    return service.get_camera_events(camera_id, limit)


@router.get("/unacknowledged/recent", response_model=List[EventResponse])
def get_recent_unacknowledged(
    limit: int = Query(50, ge=1, le=200, description="Maximum number of events to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get recent unacknowledged events.
    Requires: Any authenticated user.
    """
    service = EventService(db)
    return service.get_recent_unacknowledged(limit)


@router.get("/stats/count")
def get_event_count(
    camera_id: int = Query(None, description="Filter by camera ID"),
    event_type: str = Query(None, description="Filter by event type"),
    event_code: str = Query(None, description="Filter by event code"),
    severity: EventSeverity = Query(None, description="Filter by severity"),
    start_date: datetime = Query(None, description="Filter by start date"),
    end_date: datetime = Query(None, description="Filter by end date"),
    acknowledged: bool = Query(None, description="Filter by acknowledged status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get event count with optional filters.
    Requires: Any authenticated user.
    """
    filters = EventFilter(
        camera_id=camera_id,
        event_type=event_type,
        event_code=event_code,
        severity=severity,
        start_date=start_date,
        end_date=end_date,
        acknowledged=acknowledged,
    )
    
    service = EventService(db)
    return {"count": service.count_events(filters)}

