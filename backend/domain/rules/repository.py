"""
Rule repository - data access layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models.db.rule import Rule
from models.schemas.rule import RuleCreate, RuleUpdate


class RuleRepository:
    """Repository for rule data access operations."""
    
    def __init__(self, db: Session):
        """
        Initialize rule repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(self, rule_data: RuleCreate) -> Rule:
        """
        Create a new rule.
        
        Args:
            rule_data: Rule creation data
            
        Returns:
            Created rule instance
        """
        rule = Rule(
            name=rule_data.name,
            description=rule_data.description,
            event_code=rule_data.event_code,
            event_type=rule_data.event_type,
            is_active=rule_data.is_active,
            confidence_threshold=rule_data.confidence_threshold,
            camera_ids=rule_data.camera_ids,
            zone_config=rule_data.zone_config,
            conditions=rule_data.conditions,
            alert_config=rule_data.alert_config,
            extra_metadata=rule_data.extra_metadata,
        )
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def get_by_id(self, rule_id: int) -> Optional[Rule]:
        """
        Get rule by ID.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule instance or None if not found
        """
        return self.db.query(Rule).filter(Rule.id == rule_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        event_code: Optional[str] = None,
    ) -> List[Rule]:
        """
        Get all rules with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            event_code: Filter by event code
            
        Returns:
            List of rule instances
        """
        query = self.db.query(Rule)
        
        if is_active is not None:
            query = query.filter(Rule.is_active == is_active)
        
        if event_code:
            query = query.filter(Rule.event_code == event_code)
        
        return query.offset(skip).limit(limit).all()
    
    def update(self, rule_id: int, rule_data: RuleUpdate) -> Optional[Rule]:
        """
        Update rule.
        
        Args:
            rule_id: Rule ID
            rule_data: Rule update data
            
        Returns:
            Updated rule instance or None if not found
        """
        rule = self.get_by_id(rule_id)
        if not rule:
            return None
        
        update_data = rule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        self.db.commit()
        self.db.refresh(rule)
        return rule
    
    def delete(self, rule_id: int) -> bool:
        """
        Delete rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            True if deleted, False if not found
        """
        rule = self.get_by_id(rule_id)
        if not rule:
            return False
        
        self.db.delete(rule)
        self.db.commit()
        return True
    
    def get_by_name(self, name: str) -> Optional[Rule]:
        """
        Get rule by name.
        
        Args:
            name: Rule name
            
        Returns:
            Rule instance or None if not found
        """
        return self.db.query(Rule).filter(Rule.name == name).first()
    
    def get_active_rules(self, event_code: Optional[str] = None) -> List[Rule]:
        """
        Get all active rules.
        
        Args:
            event_code: Optional filter by event code
            
        Returns:
            List of active rule instances
        """
        query = self.db.query(Rule).filter(Rule.is_active == True)
        if event_code:
            query = query.filter(Rule.event_code == event_code)
        return query.all()
    
    def count(self, is_active: Optional[bool] = None) -> int:
        """
        Count rules.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            Number of rules
        """
        query = self.db.query(Rule)
        if is_active is not None:
            query = query.filter(Rule.is_active == is_active)
        return query.count()

