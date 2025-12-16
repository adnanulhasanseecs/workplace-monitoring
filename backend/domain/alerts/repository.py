"""
Alert repository - data access layer.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.db.alert import Alert
from models.enums import AlertStatus, NotificationChannel
from models.schemas.alert import AlertCreate


class AlertRepository:
    """Repository for alert data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize alert repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, alert_data: AlertCreate) -> Alert:
        """
        Create a new alert.
        
        Args:
            alert_data: Alert creation data
            
        Returns:
            Created alert instance
        """
        alert = Alert(
            event_id=alert_data.event_id,
            alert_rule_id=alert_data.alert_rule_id,
            channel=alert_data.channel.value,
            recipient=alert_data.recipient,
            subject=alert_data.subject,
            message=alert_data.message,
            extra_metadata=alert_data.extra_metadata,
            status=AlertStatus.PENDING.value,
        )
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
    
    def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert instance or None if not found
        """
        return self.db.query(Alert).filter(Alert.id == alert_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AlertStatus] = None,
        channel: Optional[NotificationChannel] = None,
        event_id: Optional[int] = None,
    ) -> List[Alert]:
        """
        Get all alerts with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            channel: Filter by notification channel
            event_id: Filter by event ID
            
        Returns:
            List of alert instances
        """
        query = self.db.query(Alert)
        
        if status:
            query = query.filter(Alert.status == status.value)
        
        if channel:
            query = query.filter(Alert.channel == channel.value)
        
        if event_id:
            query = query.filter(Alert.event_id == event_id)
        
        return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()
    
    def update_status(
        self,
        alert_id: int,
        status: AlertStatus,
        sent_at: Optional[datetime] = None,
    ) -> Optional[Alert]:
        """
        Update alert status.
        
        Args:
            alert_id: Alert ID
            status: New status
            sent_at: Optional timestamp when alert was sent
            
        Returns:
            Updated alert instance or None if not found
        """
        alert = self.get_by_id(alert_id)
        if not alert:
            return None
        
        alert.status = status.value
        if sent_at:
            alert.sent_at = sent_at
        
        self.db.commit()
        self.db.refresh(alert)
        return alert
    
    def acknowledge(self, alert_id: int, user_id: int) -> Optional[Alert]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            user_id: User ID who acknowledged
            
        Returns:
            Updated alert instance or None if not found
        """
        alert = self.get_by_id(alert_id)
        if not alert:
            return None
        
        alert.acknowledged = True
        alert.acknowledged_by = user_id
        alert.acknowledged_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(alert)
        return alert
    
    def get_pending(self, limit: int = 50) -> List[Alert]:
        """
        Get pending alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert instances
        """
        return (
            self.db.query(Alert)
            .filter(Alert.status == AlertStatus.PENDING.value)
            .order_by(Alert.created_at.asc())
            .limit(limit)
            .all()
        )
    
    def count(self, status: Optional[AlertStatus] = None) -> int:
        """
        Count alerts.
        
        Args:
            status: Filter by status
            
        Returns:
            Number of alerts
        """
        query = self.db.query(Alert)
        if status:
            query = query.filter(Alert.status == status.value)
        return query.count()

