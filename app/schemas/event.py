from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class EventBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    max_participants: Optional[int] = None
    points_reward: Optional[int] = 0
    is_active: Optional[bool] = True
    image_url: Optional[str] = None
    price: Optional[float] = 0.0


# Properties to receive via API on creation
class EventCreate(EventBase):
    title: str
    description: str
    event_type: str
    location: str
    start_time: datetime
    end_time: datetime


# Properties to receive via API on update
class EventUpdate(EventBase):
    pass


class EventInDBBase(EventBase):
    id: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class Event(EventInDBBase):
    pass