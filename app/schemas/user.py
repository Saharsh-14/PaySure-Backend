from pydantic import BaseModel, EmailStr
from typing import Optional


# Base schema
class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str


# Schema for user registration
class UserCreate(UserBase):
    password: str


# Schema for returning user data
class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True  # For Pydantic v2
        # If using Pydantic v1, use:
        # orm_mode = True
