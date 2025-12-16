"""
Configuration loader for event definitions and system settings.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from observability.logging import get_logger

logger = get_logger(__name__)

# Default config directory
CONFIG_DIR = Path(__file__).parent


class EventDefinition(BaseModel):
    """Event definition schema."""
    event_code: str = Field(..., description="Unique event code (e.g., 'missing_helmet')")
    event_type: str = Field(..., description="Event type category")
    name: str = Field(..., description="Human-readable event name")
    description: str = Field(..., description="Event description")
    severity: str = Field(default="medium", description="Default severity: low, medium, high, critical")
    complexity: str = Field(default="easy", description="Complexity level: easy, medium, hard")
    required_classes: Optional[List[str]] = Field(None, description="Required YOLO classes for detection")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Default confidence threshold")
    temporal_required: bool = Field(default=False, description="Whether temporal analysis is required")
    pose_required: bool = Field(default=False, description="Whether pose estimation is required")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ZoneDefinition(BaseModel):
    """Zone definition schema."""
    zone_id: str = Field(..., description="Unique zone identifier")
    name: str = Field(..., description="Zone name")
    coordinates: List[List[float]] = Field(..., description="Polygon coordinates [[x1,y1], [x2,y2], ...]")
    description: Optional[str] = Field(None, description="Zone description")
    rules: Optional[Dict[str, Any]] = Field(None, description="Zone-specific rules")


class EventConfig(BaseModel):
    """Event configuration container."""
    events: List[EventDefinition] = Field(default_factory=list, description="List of event definitions")
    zones: List[ZoneDefinition] = Field(default_factory=list, description="List of zone definitions")
    default_thresholds: Dict[str, float] = Field(default_factory=dict, description="Default thresholds by event type")


class ConfigLoader:
    """Configuration loader for event definitions and system settings."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration loader.
        
        Args:
            config_dir: Configuration directory path (defaults to config/)
        """
        self.config_dir = config_dir or CONFIG_DIR
        self._config: Optional[EventConfig] = None
    
    def load_config(self) -> EventConfig:
        """
        Load configuration from YAML files.
        
        Returns:
            EventConfig instance
            
        Raises:
            FileNotFoundError: If config files are not found
            yaml.YAMLError: If YAML parsing fails
        """
        if self._config:
            return self._config
        
        events = []
        zones = []
        default_thresholds = {}
        
        # Load event definitions
        event_files = [
            self.config_dir / "events" / "ppe_violations.yaml",
            self.config_dir / "events" / "safety_events.yaml",
            self.config_dir / "events" / "security_events.yaml",
        ]
        
        for event_file in event_files:
            if event_file.exists():
                try:
                    with open(event_file, 'r') as f:
                        data = yaml.safe_load(f)
                        if data and 'events' in data:
                            for event_data in data['events']:
                                events.append(EventDefinition(**event_data))
                        if data and 'default_thresholds' in data:
                            default_thresholds.update(data['default_thresholds'])
                    logger.info(f"Loaded events from {event_file.name}")
                except Exception as e:
                    logger.warning(f"Failed to load {event_file}: {e}")
        
        # Load zone definitions
        zone_file = self.config_dir / "zones.yaml"
        if zone_file.exists():
            try:
                with open(zone_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and 'zones' in data:
                        for zone_data in data['zones']:
                            zones.append(ZoneDefinition(**zone_data))
                logger.info(f"Loaded zones from {zone_file.name}")
            except Exception as e:
                logger.warning(f"Failed to load {zone_file}: {e}")
        
        self._config = EventConfig(
            events=events,
            zones=zones,
            default_thresholds=default_thresholds,
        )
        
        logger.info(f"Configuration loaded: {len(events)} events, {len(zones)} zones")
        return self._config
    
    def get_event_definition(self, event_code: str) -> Optional[EventDefinition]:
        """
        Get event definition by code.
        
        Args:
            event_code: Event code
            
        Returns:
            EventDefinition or None if not found
        """
        config = self.load_config()
        for event in config.events:
            if event.event_code == event_code:
                return event
        return None
    
    def get_all_events(self) -> List[EventDefinition]:
        """
        Get all event definitions.
        
        Returns:
            List of EventDefinition instances
        """
        config = self.load_config()
        return config.events
    
    def get_zone_definition(self, zone_id: str) -> Optional[ZoneDefinition]:
        """
        Get zone definition by ID.
        
        Args:
            zone_id: Zone ID
            
        Returns:
            ZoneDefinition or None if not found
        """
        config = self.load_config()
        for zone in config.zones:
            if zone.zone_id == zone_id:
                return zone
        return None
    
    def get_all_zones(self) -> List[ZoneDefinition]:
        """
        Get all zone definitions.
        
        Returns:
            List of ZoneDefinition instances
        """
        config = self.load_config()
        return config.zones
    
    def reload(self):
        """Reload configuration from files."""
        self._config = None
        self.load_config()


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader() -> ConfigLoader:
    """
    Get global configuration loader instance.
    
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

