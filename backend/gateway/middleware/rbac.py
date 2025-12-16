"""
Role-Based Access Control middleware.
"""
from fastapi import HTTPException, status
from typing import List
from models.enums import UserRole


def require_roles(allowed_roles: List[UserRole]):
    """
    Decorator to require specific roles for an endpoint.
    
    Args:
        allowed_roles: List of allowed roles
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get user from token (passed via dependency)
            user_role = kwargs.get("user_role")
            if not user_role:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )
            
            if user_role not in [role.value for role in allowed_roles]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_role(user_role: str, required_role: UserRole) -> bool:
    """
    Check if user has required role.
    
    Args:
        user_role: User's role
        required_role: Required role
        
    Returns:
        True if user has required role or higher
    """
    role_hierarchy = {
        UserRole.VIEWER: 1,
        UserRole.SUPERVISOR: 2,
        UserRole.ADMIN: 3,
    }
    
    user_level = role_hierarchy.get(UserRole(user_role), 0)
    required_level = role_hierarchy.get(required_role, 0)
    
    return user_level >= required_level


def require_role(user, allowed_roles: List[UserRole]) -> None:
    """
    Check if user has one of the required roles.
    
    Args:
        user: Current user instance (from get_current_user)
        allowed_roles: List of allowed roles
        
    Raises:
        HTTPException: If user doesn't have required role
    """
    from models.db.user import User
    
    if not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    
    user_role = UserRole(user.role)
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {[r.value for r in allowed_roles]}",
        )

