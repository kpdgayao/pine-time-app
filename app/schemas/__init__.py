"""
Schemas package initialization.
Import all schemas here to make them available when importing from app.schemas.
"""

from app.schemas.user import User, UserCreate, UserUpdate, PaginatedUserResponse
from app.schemas.token import Token, TokenPayload
from app.schemas.event import Event, EventCreate, EventUpdate, PaginatedEventResponse, EventFilterParams, PaginatedResponse
from app.schemas.badge import BadgeOut, BadgeCreate, BadgeUpdate, PaginatedBadgeResponse
from app.schemas.points import PointsTransaction, PointsTransactionCreate, PointsTransactionAdmin, PaginatedPointsTransactionResponse, PaginatedPointsTransactionAdminResponse
from app.schemas.registration import Registration, RegistrationCreate, PaginatedRegistrationResponse
from app.schemas.user_points import UserPoints, UserActivity, UserStats
from app.schemas.user_badge import UserBadgeWithProgress

__all__ = [
    "User", "UserCreate", "UserUpdate", "PaginatedUserResponse",
    "Token", "TokenPayload",
    "Event", "EventCreate", "EventUpdate", "PaginatedEventResponse", "EventFilterParams", "PaginatedResponse",
    "BadgeOut", "BadgeCreate", "BadgeUpdate", "PaginatedBadgeResponse",
    "PointsTransaction", "PointsTransactionCreate", "PaginatedPointsTransactionResponse", 
    "PointsTransactionAdmin", "PaginatedPointsTransactionAdminResponse",
    "Registration", "RegistrationCreate", "PaginatedRegistrationResponse",
    "UserPoints", "UserActivity", "UserStats",
    "UserBadgeWithProgress"
]
