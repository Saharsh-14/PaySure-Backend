from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT

class UserCreate(UserBase):
    clerk_id: str

class UserResponse(UserBase):
    clerk_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
