from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class RegistrationBase(BaseModel):
    event_id: Optional[int] = None
    status: Optional[str] = "registered"
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

    class Config:
        from_attributes = True


# Additional properties to return via API
class Registration(RegistrationInDBBase):
    pass