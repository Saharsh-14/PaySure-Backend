from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, description="The title of the project")
    description: Optional[str] = Field(None, max_length=1000, description="Detailed description of the project requirements")

class ProjectCreate(ProjectBase):
    other_party_email: str = Field(..., description="Email of the client or freelancer to assign to the project")

class ProjectResponse(ProjectBase):
    id: int
    client_id: str
    freelancer_id: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
