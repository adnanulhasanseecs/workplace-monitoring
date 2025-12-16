"""
Event domain module.
"""
from domain.events.repository import EventRepository
from domain.events.service import EventService

__all__ = ["EventRepository", "EventService"]

