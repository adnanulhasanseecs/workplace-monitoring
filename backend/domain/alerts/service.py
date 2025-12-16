"""
Alert domain service - business logic layer.
"""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from models.db.alert import Alert
from models.enums import AlertStatus, NotificationChannel
from models.schemas.alert import AlertCreate, AlertResponse
from domain.alerts.repository import AlertRepository
from observability.logging import get_logger

logger = get_logger(__name__)


class AlertService:
    """Service for alert business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize alert service.
        
        Args:
            db: Database session
        """
        self.repository = AlertRepository(db)
        self.db = db
    
    def create_alert(self, alert_data: AlertCreate) -> AlertResponse:
        """
        Create a new alert.
        
        Args:
            alert_data: Alert creation data
            
        Returns:
            Created alert response
        """
        alert = self.repository.create(alert_data)
        logger.info(
            "Alert created",
            extra={
                "alert_id": alert.id,
                "channel": alert.channel,
                "recipient": alert.recipient,
                "event_id": alert.event_id,
            }
        )
        return AlertResponse.model_validate(alert)
    
    def get_alert(self, alert_id: int) -> Optional[AlertResponse]:
        """
        Get alert by ID.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Alert response or None if not found
        """
        alert = self.repository.get_by_id(alert_id)
        if not alert:
            return None
        return AlertResponse.model_validate(alert)
    
    def list_alerts(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[AlertStatus] = None,
        channel: Optional[NotificationChannel] = None,
        event_id: Optional[int] = None,
    ) -> List[AlertResponse]:
        """
        List alerts with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status
            channel: Filter by notification channel
            event_id: Filter by event ID
            
        Returns:
            List of alert responses
        """
        alerts = self.repository.get_all(
            skip=skip,
            limit=limit,
            status=status,
            channel=channel,
            event_id=event_id,
        )
        return [AlertResponse.model_validate(alert) for alert in alerts]
    
    def mark_sent(self, alert_id: int) -> Optional[AlertResponse]:
        """
        Mark alert as sent.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Updated alert response or None if not found
        """
        alert = self.repository.update_status(alert_id, AlertStatus.SENT, datetime.utcnow())
        if alert:
            logger.info("Alert marked as sent", extra={"alert_id": alert_id})
            return AlertResponse.model_validate(alert)
        return None
    
    def mark_failed(self, alert_id: int) -> Optional[AlertResponse]:
        """
        Mark alert as failed.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            Updated alert response or None if not found
        """
        alert = self.repository.update_status(alert_id, AlertStatus.FAILED)
        if alert:
            logger.warning("Alert marked as failed", extra={"alert_id": alert_id})
            return AlertResponse.model_validate(alert)
        return None
    
    def acknowledge_alert(self, alert_id: int, user_id: int) -> Optional[AlertResponse]:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            user_id: User ID who acknowledged
            
        Returns:
            Updated alert response or None if not found
        """
        alert = self.repository.acknowledge(alert_id, user_id)
        if alert:
            logger.info("Alert acknowledged", extra={"alert_id": alert_id, "user_id": user_id})
            return AlertResponse.model_validate(alert)
        return None
    
    def get_pending_alerts(self, limit: int = 50) -> List[AlertResponse]:
        """
        Get pending alerts.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert responses
        """
        alerts = self.repository.get_pending(limit)
        return [AlertResponse.model_validate(alert) for alert in alerts]
    
    def get_alert_count(self, status: Optional[AlertStatus] = None) -> int:
        """
        Get total alert count.
        
        Args:
            status: Filter by status
            
        Returns:
            Number of alerts
        """
        return self.repository.count(status=status)

