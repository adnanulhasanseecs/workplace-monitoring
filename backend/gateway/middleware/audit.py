"""
Audit logging middleware.
"""
from fastapi import Request
from typing import Callable
import time

from observability.logging import get_logger

logger = get_logger(__name__)


async def audit_middleware(request: Request, call_next: Callable):
    """
    Audit logging middleware.
    Logs all requests for compliance.
    
    Args:
        request: FastAPI request
        call_next: Next middleware/route handler
        
    Returns:
        Response
    """
    start_time = time.time()
    
    # Get user info from token if available
    user_id = None
    username = None
    if "authorization" in request.headers:
        try:
            from app.core.security import decode_access_token
            token = request.headers["authorization"].replace("Bearer ", "")
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")
                username = payload.get("username")
        except Exception:
            pass
    
    # Process request
    response = await call_next(request)
    
    # Log audit event
    duration = time.time() - start_time
    logger.info(
        "request_processed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        user_id=user_id,
        username=username,
        ip_address=request.client.host if request.client else None,
        duration_ms=duration * 1000,
    )
    
    return response

