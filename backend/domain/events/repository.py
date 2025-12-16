"""
Event repository - data access layer.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from models.db.event import Event
from models.enums import EventType, EventSeverity
from models.schemas.event import EventCreate, EventFilter


class EventRepository:
    """Repository for event data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize event repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, event_data: EventCreate) -> Event:
        """
        Create a new event.
        
        Args:
            event_data: Event creation data
            
        Returns:
            Created event instance
        """
        event = Event(
            camera_id=event_data.camera_id,
            event_type=event_data.event_type,
            event_code=event_data.event_code,
            severity=event_data.severity.value,
            confidence=event_data.confidence,
            timestamp=event_data.timestamp,
            frame_number=event_data.frame_number,
            clip_path=event_data.clip_path,
            extra_metadata=event_data.extra_metadata,
            description=event_data.description,
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_by_id(self, event_id: int) -> Optional[Event]:
        """
        Get event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event instance or None if not found
        """
        return self.db.query(Event).filter(Event.id == event_id).first()
    
    def get_all(self, filters: EventFilter) -> List[Event]:
        """
        Get events with filters.
        
        Args:
            filters: Event filter criteria
            
        Returns:
            List of event instances
        """
        query = self.db.query(Event)
        
        if filters.camera_id:
            query = query.filter(Event.camera_id == filters.camera_id)
        
        if filters.event_type:
            query = query.filter(Event.event_type == filters.event_type)
        
        if filters.event_code:
            query = query.filter(Event.event_code == filters.event_code)
        
        if filters.severity:
            query = query.filter(Event.severity == filters.severity.value)
        
        if filters.start_date:
            query = query.filter(Event.timestamp >= filters.start_date)
        
        if filters.end_date:
            query = query.filter(Event.timestamp <= filters.end_date)
        
        if filters.acknowledged is not None:
            query = query.filter(Event.acknowledged == filters.acknowledged)
        
        return query.order_by(Event.timestamp.desc()).offset(filters.offset).limit(filters.limit).all()
    
    def count(self, filters: Optional[EventFilter] = None) -> int:
        """
        Count events with optional filters.
        
        Args:
            filters: Optional event filter criteria
            
        Returns:
            Number of events
        """
        query = self.db.query(Event)
        
        if filters:
            if filters.camera_id:
                query = query.filter(Event.camera_id == filters.camera_id)
            if filters.event_type:
                query = query.filter(Event.event_type == filters.event_type)
            if filters.event_code:
                query = query.filter(Event.event_code == filters.event_code)
            if filters.severity:
                query = query.filter(Event.severity == filters.severity.value)
            if filters.start_date:
                query = query.filter(Event.timestamp >= filters.start_date)
            if filters.end_date:
                query = query.filter(Event.timestamp <= filters.end_date)
            if filters.acknowledged is not None:
                query = query.filter(Event.acknowledged == filters.acknowledged)
        
        return query.count()
    
    def acknowledge(self, event_id: int, user_id: int) -> Optional[Event]:
        """
        Acknowledge an event.
        
        Args:
            event_id: Event ID
            user_id: User ID who acknowledged
            
        Returns:
            Updated event instance or None if not found
        """
        event = self.get_by_id(event_id)
        if not event:
            return None
        
        event.acknowledged = True
        event.acknowledged_by = user_id
        event.acknowledged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(event)
        return event
    
    def get_by_camera(self, camera_id: int, limit: int = 100) -> List[Event]:
        """
        Get events for a specific camera.
        
        Args:
            camera_id: Camera ID
            limit: Maximum number of events to return
            
        Returns:
            List of event instances
        """
        return (
            self.db.query(Event)
            .filter(Event.camera_id == camera_id)
            .order_by(Event.timestamp.desc())
            .limit(limit)
            .all()
        )
    
    def get_recent_unacknowledged(self, limit: int = 50) -> List[Event]:
        """
        Get recent unacknowledged events.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of event instances
        """
        return (
            self.db.query(Event)
            .filter(Event.acknowledged == False)
            .order_by(Event.timestamp.desc())
            .limit(limit)
            .all()
        )

