from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.schemas.event import PaginatedResponse


# Shared properties
class RegistrationBase(BaseModel):
    event_id: Optional[int] = None
    # status: 'pending', 'approved', 'rejected', 'cancelled', etc.
    status: Optional[str] = "pending"
    payment_status: Optional[str] = "pending"


# Properties to receive via API on creation
class RegistrationCreate(RegistrationBase):
    event_id: int
    user_id: Optional[int] = None


# Properties to receive via API on update
class RegistrationUpdate(RegistrationBase):
    pass


class RegistrationInDBBase(RegistrationBase):
    id: int
    user_id: int
    registration_date: datetime
    user: Optional['User'] = None
    event: Optional['Event'] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class Registration(RegistrationInDBBase):
    pass


# Paginated response for registration listings
class PaginatedRegistrationResponse(PaginatedResponse[Registration]):
    """
    Paginated response specifically for registrations
    """


from app.schemas.user import User
from app.schemas.event import Event

RegistrationInDBBase.update_forward_refs()
Registration.update_forward_refs()