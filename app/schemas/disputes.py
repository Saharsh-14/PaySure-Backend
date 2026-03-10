from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DisputeBase(BaseModel):
    reason: str = Field(..., min_length=10, max_length=2000, description="Detailed reason for raising the dispute")


class DisputeCreate(DisputeBase):
    milestone_id: int


class DisputeResponse(DisputeBase):
    id: int
    milestone_id: int
    raised_by: str
    status: str
    resolution_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
