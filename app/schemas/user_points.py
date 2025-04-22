from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class UserPoints(BaseModel):
    """Schema for user points response"""
    points: int
    user_id: int

    class Config:
        orm_mode = True


class UserActivity(BaseModel):
    """Schema for user activity"""
    id: int
    type: str  # "points", "badge", "event", etc.
    description: str
    points: Optional[int] = None
    date: datetime
    event_id: Optional[int] = None

    class Config:
        orm_mode = True


class UserStats(BaseModel):
    """Schema for comprehensive user statistics"""
    total_points: int
    total_badges: int
    rank: int
    total_users: int
    streak_count: int
    events_attended: int
    recent_activities: List[Dict[str, Any]]

    class Config:
        orm_mode = True
