from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DisputeBase(BaseModel):
    reason: str


class DisputeCreate(DisputeBase):
    milestone_id: int


class DisputeResponse(DisputeBase):
    id: int
    milestone_id: int
    raised_by: int
    status: str
    resolution_note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2
