"""
Rule domain service - business logic layer.
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from models.db.rule import Rule
from models.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from domain.rules.repository import RuleRepository
from observability.logging import get_logger

logger = get_logger(__name__)


class RuleService:
    """Service for rule business logic."""
    
    def __init__(self, db: Session):
        """
        Initialize rule service.
        
        Args:
            db: Database session
        """
        self.repository = RuleRepository(db)
        self.db = db
    
    def create_rule(self, rule_data: RuleCreate) -> RuleResponse:
        """
        Create a new rule with validation.
        
        Args:
            rule_data: Rule creation data
            
        Returns:
            Created rule response
            
        Raises:
            ValueError: If rule name already exists
        """
        # Check for duplicate name
        existing = self.repository.get_by_name(rule_data.name)
        if existing:
            raise ValueError(f"Rule with name '{rule_data.name}' already exists")
        
        rule = self.repository.create(rule_data)
        logger.info("Rule created", extra={"rule_id": rule.id, "name": rule.name, "event_code": rule.event_code})
        return RuleResponse.model_validate(rule)
    
    def get_rule(self, rule_id: int) -> Optional[RuleResponse]:
        """
        Get rule by ID.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Rule response or None if not found
        """
        rule = self.repository.get_by_id(rule_id)
        if not rule:
            return None
        return RuleResponse.model_validate(rule)
    
    def list_rules(
        self,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        event_code: Optional[str] = None,
    ) -> List[RuleResponse]:
        """
        List rules with optional filters.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            is_active: Filter by active status
            event_code: Filter by event code
            
        Returns:
            List of rule responses
        """
        rules = self.repository.get_all(skip=skip, limit=limit, is_active=is_active, event_code=event_code)
        return [RuleResponse.model_validate(rule) for rule in rules]
    
    def update_rule(self, rule_id: int, rule_data: RuleUpdate) -> Optional[RuleResponse]:
        """
        Update rule with validation.
        
        Args:
            rule_id: Rule ID
            rule_data: Rule update data
            
        Returns:
            Updated rule response or None if not found
            
        Raises:
            ValueError: If new name conflicts with existing rule
        """
        # Check if rule exists
        existing = self.repository.get_by_id(rule_id)
        if not existing:
            return None
        
        # Check for duplicate name if name is being updated
        if rule_data.name and rule_data.name != existing.name:
            duplicate = self.repository.get_by_name(rule_data.name)
            if duplicate:
                raise ValueError(f"Rule with name '{rule_data.name}' already exists")
        
        rule = self.repository.update(rule_id, rule_data)
        if rule:
            logger.info("Rule updated", extra={"rule_id": rule.id, "name": rule.name})
            return RuleResponse.model_validate(rule)
        return None
    
    def delete_rule(self, rule_id: int) -> bool:
        """
        Delete rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            True if deleted, False if not found
        """
        rule = self.repository.get_by_id(rule_id)
        if not rule:
            return False
        
        success = self.repository.delete(rule_id)
        if success:
            logger.info("Rule deleted", extra={"rule_id": rule_id, "name": rule.name})
        return success
    
    def get_active_rules(self, event_code: Optional[str] = None) -> List[RuleResponse]:
        """
        Get all active rules.
        
        Args:
            event_code: Optional filter by event code
            
        Returns:
            List of active rule responses
        """
        rules = self.repository.get_active_rules(event_code)
        return [RuleResponse.model_validate(rule) for rule in rules]
    
    def activate_rule(self, rule_id: int) -> Optional[RuleResponse]:
        """
        Activate a rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Updated rule response or None if not found
        """
        rule = self.repository.update(rule_id, RuleUpdate(is_active=True))
        if rule:
            logger.info("Rule activated", extra={"rule_id": rule.id})
            return RuleResponse.model_validate(rule)
        return None
    
    def deactivate_rule(self, rule_id: int) -> Optional[RuleResponse]:
        """
        Deactivate a rule.
        
        Args:
            rule_id: Rule ID
            
        Returns:
            Updated rule response or None if not found
        """
        rule = self.repository.update(rule_id, RuleUpdate(is_active=False))
        if rule:
            logger.info("Rule deactivated", extra={"rule_id": rule.id})
            return RuleResponse.model_validate(rule)
        return None
    
    def get_rule_count(self, is_active: Optional[bool] = None) -> int:
        """
        Get total rule count.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            Number of rules
        """
        return self.repository.count(is_active=is_active)

