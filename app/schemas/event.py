from typing import Optional, List, Literal, Any, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel, Field


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


# Event filtering parameters
class EventFilterParams(BaseModel):
    """
    Parameters for filtering events, matching frontend EventFilters component.
    """
    search: Optional[str] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    sort_by: Optional[Literal["start-soonest", "start-latest", "title-az", "price-low", "price-high"]] = "start-soonest"
    skip: Optional[int] = 0
    limit: Optional[int] = 100


# Define a TypeVar for generic item types
T = TypeVar('T')

# Simplified pagination schema for list endpoints
class PaginatedResponse(BaseModel, Generic[T]):
    """
    Standard paginated response format
    """
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        arbitrary_types_allowed = True
        from_attributes = True


class EventInDBBase(EventBase):
    id: int

    class Config:
        from_attributes = True


# Additional properties to return via API

class EventStats(BaseModel):
    """
    Schema for event statistics returned by /events/{event_id}/stats endpoint.
    """
    event_id: int
    registration_count: int
    total_revenue: float
    unique_participants: int
    # Add more fields as needed for stats

    class Config:
        from_attributes = True


class Event(EventInDBBase):
    pass


class PaginatedEventResponse(PaginatedResponse[Event]):
    """
    Paginated response specifically for events
    """