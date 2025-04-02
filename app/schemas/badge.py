from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class BadgeBase(BaseModel):
    badge_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


# Properties to receive via API on creation
class BadgeCreate(BadgeBase):
    badge_type: str
    name: str
    description: str


# Properties to receive via API on update
class BadgeUpdate(BadgeBase):
    pass


class BadgeInDBBase(BadgeBase):
    id: int
    user_id: int
    earned_date: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class Badge(BadgeInDBBase):
    pass