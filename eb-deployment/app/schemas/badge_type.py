from typing import Optional
from pydantic import BaseModel

class BadgeTypeBase(BaseModel):
    badge_type: str
    name: str
    description: Optional[str] = None
    criteria_type: Optional[str] = None
    criteria_threshold: Optional[int] = None
    level: Optional[str] = None
    image_url: Optional[str] = None

class BadgeTypeCreate(BadgeTypeBase):
    pass

class BadgeTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria_type: Optional[str] = None
    criteria_threshold: Optional[int] = None
    level: Optional[str] = None
    image_url: Optional[str] = None

from pydantic import ConfigDict

class BadgeTypeOut(BadgeTypeBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
