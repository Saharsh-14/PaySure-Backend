from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.milestone import MilestoneStatus


# Base milestone schema
class MilestoneBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Amount to be placed in escrow for this milestone")


# Used when creating milestone
class MilestoneCreate(MilestoneBase):
    project_id: int


# Used when returning milestone data
class MilestoneResponse(MilestoneBase):
    id: int
    project_id: int
    status: MilestoneStatus
    created_at: datetime
    last_updated_by: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
