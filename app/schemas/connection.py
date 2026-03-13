from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.connection import ConnectionStatus

class ConnectionInviteRequest(BaseModel):
    email: EmailStr

class ConnectionResponse(BaseModel):
    id: int
    sender_id: str
    recipient_id: str
    client_id: str
    freelancer_id: str
    status: ConnectionStatus
    created_at: datetime
    
    # Extra fields for UI convenience
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
