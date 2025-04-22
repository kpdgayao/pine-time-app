from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class UserBadgeWithProgress(BaseModel):
    """Schema for user badge with progress information"""
    id: int
    badge_id: int
    user_id: int
    level: int = 1
    earned_date: Optional[datetime] = None
    
    # Progress fields
    progress: Optional[int] = None
    next_level_threshold: Optional[int] = None
    is_new: Optional[bool] = False
    
    # Badge details
    name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    category: Optional[str] = None

    class Config:
        orm_mode = True
