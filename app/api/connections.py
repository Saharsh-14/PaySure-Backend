from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.user import User, UserRole
from app.models.connection import Connection, ConnectionStatus
from app.schemas.connection import ConnectionInviteRequest, ConnectionResponse
from app.api.deps import get_current_user, CurrentUser

router = APIRouter(prefix="/connections", tags=["Connections"])

def _format_connection(conn: Connection) -> ConnectionResponse:
    """Helper to inject names and emails into the response."""
    res = ConnectionResponse.model_validate(conn)
    if conn.sender:
        res.sender_name = conn.sender.full_name
        res.sender_email = conn.sender.email
    if conn.recipient:
        res.recipient_name = conn.recipient.full_name
        res.recipient_email = conn.recipient.email
    return res

@router.post("/invite", response_model=ConnectionResponse)
def invite_partner(
    request: ConnectionInviteRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Invites a professional to connect. Only Clients can initiate invitations.
    """
    # 0. Role check: Only Clients can invite
    current_role_str = str(current_user.role).lower()
    if current_role_str != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Clients can initiate invitations. Freelancers should wait for invitations."
        )

    # 1. Find user by email (with JIT sync)
    from app.services.user_service import get_or_sync_user
    recipient = get_or_sync_user(db, request.email)
    
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. They must register with Clerk first."
        )

    # 2. Check roles (recipient must be Freelancer)
    recipient_role_str = recipient.role.value if hasattr(recipient.role, 'value') else str(recipient.role)
    if recipient_role_str.lower() != "freelancer":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only invite Freelancers to connect."
        )

    # 3. Check if already connected or pending
    existing = db.query(Connection).filter(
        ((Connection.sender_id == current_user.clerk_id) & (Connection.recipient_id == recipient.clerk_id)) |
        ((Connection.sender_id == recipient.clerk_id) & (Connection.recipient_id == current_user.clerk_id))
    ).first()

    if existing:
        return _format_connection(existing)

    # 4. Create Connection (Pending)
    new_connection = Connection(
        sender_id=current_user.clerk_id,
        recipient_id=recipient.clerk_id,
        client_id=current_user.clerk_id,
        freelancer_id=recipient.clerk_id,
        status=ConnectionStatus.PENDING
    )

    try:
        db.add(new_connection)
        db.commit()
        db.refresh(new_connection)
        return _format_connection(new_connection)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create invitation."
        )

@router.post("/{connection_id}/accept", response_model=ConnectionResponse)
def accept_invitation(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Accept a pending invitation."""
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        Connection.recipient_id == current_user.clerk_id,
        Connection.status == ConnectionStatus.PENDING
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Pending invitation not found.")

    connection.status = ConnectionStatus.ACTIVE
    db.commit()
    db.refresh(connection)
    return _format_connection(connection)

@router.post("/{connection_id}/reject", response_model=dict)
def reject_invitation(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Reject or cancel an invitation."""
    connection = db.query(Connection).filter(
        Connection.id == connection_id,
        (Connection.recipient_id == current_user.clerk_id) | (Connection.sender_id == current_user.clerk_id)
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Invitation not found.")

    db.delete(connection)
    db.commit()
    return {"message": "Invitation removed."}

@router.get("/my", response_model=List[ConnectionResponse])
def get_my_connections(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    """Fetch all active/pending connections with partner details."""
    connections = db.query(Connection).filter(
        (Connection.sender_id == current_user.clerk_id) | (Connection.recipient_id == current_user.clerk_id)
    ).all()
    
    return [_format_connection(c) for c in connections]
