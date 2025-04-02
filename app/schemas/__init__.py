"""
Schemas package initialization.
Import all schemas here to make them available when importing from app.schemas.
"""

from app.schemas.user import User, UserCreate, UserUpdate
from app.schemas.token import Token, TokenPayload
from app.schemas.event import Event, EventCreate, EventUpdate
from app.schemas.badge import Badge, BadgeCreate, BadgeUpdate
from app.schemas.points import PointsTransaction, PointsTransactionCreate
from app.schemas.registration import Registration, RegistrationCreate

__all__ = [
    "User", "UserCreate", "UserUpdate",
    "Token", "TokenPayload",
    "Event", "EventCreate", "EventUpdate",
    "Badge", "BadgeCreate", "BadgeUpdate",
    "PointsTransaction", "PointsTransactionCreate",
    "Registration", "RegistrationCreate"
]
