from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# Base milestone schema
class MilestoneBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: float


# Used when creating milestone
class MilestoneCreate(MilestoneBase):
    project_id: int


# Used when returning milestone data
class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
        # For v1 use:
        # orm_mode = True
