from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.connection import Connection, ConnectionStatus
from app.schemas.connection import ConnectionInviteRequest, ConnectionResponse
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.post("/invite", response_model=ConnectionResponse)
def invite_partner(
    request: ConnectionInviteRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    # 1. Find user by email
    recipient = db.query(User).filter(User.email == request.email).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. They must register with PaySure first."
        )

    # 2. Check roles (must be opposite)
    if recipient.role == current_user.role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You can only connect with { 'Freelancers' if current_user.role == 'Client' else 'Clients' }."
        )

    # 3. Check if already connected
    existing = db.query(Connection).filter(
        ((Connection.sender_id == current_user.clerk_id) & (Connection.recipient_id == recipient.clerk_id)) |
        ((Connection.sender_id == recipient.clerk_id) & (Connection.recipient_id == current_user.clerk_id))
    ).first()

    if existing:
        return existing

    # 4. Create Connection
    client_id = current_user.clerk_id if current_user.role == "Client" else recipient.clerk_id
    freelancer_id = current_user.clerk_id if current_user.role == "Freelancer" else recipient.clerk_id

    new_connection = Connection(
        sender_id=current_user.clerk_id,
        recipient_id=recipient.clerk_id,
        client_id=client_id,
        freelancer_id=freelancer_id,
        status=ConnectionStatus.ACTIVE # Auto-active for this phase
    )

    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)

    return new_connection

@router.get("/my", response_model=List[ConnectionResponse])
def get_my_connections(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    connections = db.query(Connection).filter(
        (Connection.sender_id == current_user.clerk_id) | (Connection.recipient_id == current_user.clerk_id)
    ).all()
    return connections
