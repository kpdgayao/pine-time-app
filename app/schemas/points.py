from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class PointsTransactionBase(BaseModel):
    points: Optional[int] = None
    transaction_type: Optional[str] = None
    description: Optional[str] = None
    event_id: Optional[int] = None


# Properties to receive via API on creation
class PointsTransactionCreate(PointsTransactionBase):
    points: int
    transaction_type: str
    description: str


# Properties to receive via API on update
class PointsTransactionUpdate(PointsTransactionBase):
    pass


class PointsTransactionInDBBase(PointsTransactionBase):
    id: int
    user_id: int
    transaction_date: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class PointsTransaction(PointsTransactionInDBBase):
    pass

from .user import User
from .event import Event
from typing import Optional

class PointsTransactionAdmin(PointsTransactionInDBBase):
    user: Optional[User] = None
    event: Optional[Event] = None
    admin: Optional[User] = None  # If you have an admin_id/admin relationship

    class Config:
        from_attributes = True