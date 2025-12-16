"""
Rate limiting middleware.
"""
from fastapi import HTTPException, status, Request
from typing import Callable
import time
from collections import defaultdict

from app.core.config import settings

# In-memory rate limit store (use Redis in production)
rate_limit_store = defaultdict(list)


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """
    Rate limiting decorator.
    
    Args:
        max_requests: Maximum requests per window
        window_seconds: Time window in seconds
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable):
        async def wrapper(request: Request, *args, **kwargs):
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()
            
            # Clean old entries
            rate_limit_store[client_ip] = [
                timestamp
                for timestamp in rate_limit_store[client_ip]
                if current_time - timestamp < window_seconds
            ]
            
            # Check rate limit
            if len(rate_limit_store[client_ip]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )
            
            # Record request
            rate_limit_store[client_ip].append(current_time)
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

