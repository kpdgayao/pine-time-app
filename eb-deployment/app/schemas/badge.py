from typing import Optional
from datetime import datetime
from pydantic import BaseModel


from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from .badge_type import BadgeTypeOut

class BadgeBase(BaseModel):
    badge_type_id: int
    level: Optional[str] = None

class BadgeCreate(BadgeBase):
    user_id: int
    level: Optional[str] = None

class BadgeUpdate(BaseModel):
    level: Optional[str] = None

class BadgeAssign(BaseModel):
    user_id: int
    badge_type_id: int
    level: Optional[str] = None

class BadgeRevoke(BaseModel):
    user_id: int
    badge_id: int

class BadgeInDBBase(BadgeBase):
    id: int
    user_id: int
    earned_date: datetime
    level: Optional[str] = None

    class Config:
        from_attributes = True

from pydantic import ConfigDict

class BadgeOut(BadgeInDBBase):
    badge_type_obj: Optional[BadgeTypeOut]
    model_config = ConfigDict(from_attributes=True)