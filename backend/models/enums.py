"""
Shared enumerations for the application.
"""
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    VIEWER = "viewer"


class EventType(str, Enum):
    """Event type categories."""
    PPE_VIOLATION = "ppe_violation"
    SAFETY_INCIDENT = "safety_incident"
    SECURITY_EVENT = "security_event"
    BEHAVIOR_ANOMALY = "behavior_anomaly"
    EQUIPMENT_MISUSE = "equipment_misuse"


class EventSeverity(str, Enum):
    """Event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    """Alert status."""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class CameraStatus(str, Enum):
    """Camera status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    ERROR = "error"


class NotificationChannel(str, Enum):
    """Notification channels."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class ProcessingStatus(str, Enum):
    """Video processing job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

