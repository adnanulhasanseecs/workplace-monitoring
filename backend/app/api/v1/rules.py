"""
Rule configuration API endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from gateway.middleware.auth import get_current_user
from gateway.middleware.rbac import require_role
from models.db.user import User
from models.enums import UserRole
from models.schemas.rule import RuleCreate, RuleUpdate, RuleResponse
from domain.rules.service import RuleService

router = APIRouter(prefix="/rules", tags=["rules"])


@router.post("", response_model=RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule_data: RuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new rule.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = RuleService(db)
    try:
        return service.create_rule(rule_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=List[RuleResponse])
def list_rules(
    skip: int = Query(0, ge=0, description="Number of rules to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of rules to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    event_code: Optional[str] = Query(None, description="Filter by event code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List rules with optional filters.
    Requires: Any authenticated user.
    """
    service = RuleService(db)
    return service.list_rules(skip=skip, limit=limit, is_active=is_active, event_code=event_code)


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get rule by ID.
    Requires: Any authenticated user.
    """
    service = RuleService(db)
    rule = service.get_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update rule.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = RuleService(db)
    try:
        rule = service.update_rule(rule_id, rule_data)
        if not rule:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
        return rule
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete rule.
    Requires: Admin role.
    """
    require_role(current_user, [UserRole.ADMIN])
    
    service = RuleService(db)
    success = service.delete_rule(rule_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")


@router.get("/active/list", response_model=List[RuleResponse])
def get_active_rules(
    event_code: Optional[str] = Query(None, description="Filter by event code"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all active rules.
    Requires: Any authenticated user.
    """
    service = RuleService(db)
    return service.get_active_rules(event_code)


@router.post("/{rule_id}/activate", response_model=RuleResponse)
def activate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Activate a rule.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = RuleService(db)
    rule = service.activate_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.post("/{rule_id}/deactivate", response_model=RuleResponse)
def deactivate_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Deactivate a rule.
    Requires: Supervisor or Admin role.
    """
    require_role(current_user, [UserRole.SUPERVISOR, UserRole.ADMIN])
    
    service = RuleService(db)
    rule = service.deactivate_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return rule


@router.get("/stats/count")
def get_rule_count(
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get rule count.
    Requires: Any authenticated user.
    """
    service = RuleService(db)
    return {"count": service.get_rule_count(is_active=is_active)}

