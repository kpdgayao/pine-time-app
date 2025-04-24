from typing import Optional, List
from pydantic import BaseModel, EmailStr
from app.schemas.event import PaginatedResponse


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    user_type: Optional[str] = "regular"


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    username: str
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Paginated response for user listings
class PaginatedUserResponse(PaginatedResponse):
    """
    Paginated response specifically for users
    """


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str