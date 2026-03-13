from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.disputes import DisputeCreate
from app.crud.disputes import (
    create_dispute,
    get_disputes_by_milestone,
    resolve_dispute
)
from app.models.disputes import Dispute
from app.crud.milestone import get_milestone_by_id
from app.services.notification_service import send_notification
from app.core.logger import logger

from app.services.milestone_service import dispute_milestone_service

def raise_dispute_service(db: Session, dispute: DisputeCreate, current_user):
    """Business logic for raising a dispute."""
    milestone = get_milestone_by_id(db, dispute.milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    # Freeze milestone status
    dispute_milestone_service(db, dispute.milestone_id, current_user)

    # Record the dispute
    dispute_record = create_dispute(
        db,
        milestone_id=dispute.milestone_id,
        clerk_id=current_user.clerk_id,
        reason=dispute.reason
    )

    # Note: A real app would get project.client_id and project.freelancer_id to notify both
    send_notification(current_user.id, "Dispute Raised", f"Your dispute for milestone #{dispute.milestone_id} has been recorded.")

    logger.warning(
        "dispute_raised",
        dispute_id=dispute_record.id,
        milestone_id=dispute.milestone_id,
        raised_by=current_user.id,
        reason=dispute.reason
    )

    return dispute_record

def get_milestone_disputes_service(db: Session, milestone_id: int):
    """Business logic for getting disputes of a milestone."""
    return get_disputes_by_milestone(db, milestone_id)

def resolve_dispute_api_service(db: Session, dispute_id: int, resolution_note: str, current_user):
    """Business logic for an admin to resolve a dispute."""
    resolved_dispute = resolve_dispute(db, dispute_id, resolution_note)
    
    if resolved_dispute:
        send_notification(resolved_dispute.raised_by, "Dispute Resolved", f"Your dispute #{dispute_id} was resolved.")
        
        logger.info(
            "dispute_resolved",
            dispute_id=dispute_id,
            resolved_by=current_user.id,
            resolution_note=resolution_note
        )

    return resolved_dispute
