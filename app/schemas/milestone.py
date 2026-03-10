from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# Base milestone schema
class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: float = Field(..., gt=0, description="Amount to be placed in escrow for this milestone")


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
