"""
Models package initialization.
Import all models here to make them available when importing from app.models.
"""

from app.models.user import User
from app.models.event import Event
from app.models.badge import Badge
from app.models.points import PointsTransaction
from app.models.registration import Registration
from app.models.badge_type import BadgeType
from app.models.user_badge import UserBadge
from app.models.event_attendee import EventAttendee

__all__ = [
    "User", "Event", "Badge", "PointsTransaction", "Registration", "BadgeType",
    "UserBadge", "EventAttendee"
]
