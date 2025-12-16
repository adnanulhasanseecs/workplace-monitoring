"""
Event domain service - business logic layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models.db.event import Event
from models.schemas.event import EventCreate, EventResponse, EventFilter
from domain.events.repository import EventRepository
from observability.logging import get_logger

logger = get_logger(__name__)


class EventService:
    """Service for event business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize event service.
        
        Args:
            db: Database session
        """
        self.repository = EventRepository(db)
        self.db = db
    
    def create_event(self, event_data: EventCreate) -> EventResponse:
        """
        Create a new event.
        
        Args:
            event_data: Event creation data
            
        Returns:
            Created event response
        """
        event = self.repository.create(event_data)
        logger.info(
            "Event created",
            extra={
                "event_id": event.id,
                "event_type": event.event_type,
                "event_code": event.event_code,
                "camera_id": event.camera_id,
            }
        )
        return EventResponse.model_validate(event)
    
    def get_event(self, event_id: int) -> Optional[EventResponse]:
        """
        Get event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event response or None if not found
        """
        event = self.repository.get_by_id(event_id)
        if not event:
            return None
        return EventResponse.model_validate(event)
    
    def list_events(self, filters: EventFilter) -> List[EventResponse]:
        """
        List events with filters.
        
        Args:
            filters: Event filter criteria
            
        Returns:
            List of event responses
        """
        events = self.repository.get_all(filters)
        return [EventResponse.model_validate(event) for event in events]
    
    def count_events(self, filters: Optional[EventFilter] = None) -> int:
        """
        Count events with optional filters.
        
        Args:
            filters: Optional event filter criteria
            
        Returns:
            Number of events
        """
        return self.repository.count(filters)
    
    def acknowledge_event(self, event_id: int, user_id: int) -> Optional[EventResponse]:
        """
        Acknowledge an event.
        
        Args:
            event_id: Event ID
            user_id: User ID who acknowledged
            
        Returns:
            Updated event response or None if not found
        """
        event = self.repository.acknowledge(event_id, user_id)
        if event:
            logger.info("Event acknowledged", extra={"event_id": event_id, "user_id": user_id})
            return EventResponse.model_validate(event)
        return None
    
    def get_camera_events(self, camera_id: int, limit: int = 100) -> List[EventResponse]:
        """
        Get events for a specific camera.
        
        Args:
            camera_id: Camera ID
            limit: Maximum number of events to return
            
        Returns:
            List of event responses
        """
        events = self.repository.get_by_camera(camera_id, limit)
        return [EventResponse.model_validate(event) for event in events]
    
    def get_recent_unacknowledged(self, limit: int = 50) -> List[EventResponse]:
        """
        Get recent unacknowledged events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event responses
        """
        events = self.repository.get_recent_unacknowledged(limit)
        return [EventResponse.model_validate(event) for event in events]

