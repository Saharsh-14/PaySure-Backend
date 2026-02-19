from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.disputes import DisputeCreate, DisputeResponse
from app.crud.disputes import (
    create_dispute,
    get_disputes_by_milestone,
    resolve_dispute
)
from app.crud.milestone import get_milestone_by_id

router = APIRouter(prefix="/disputes", tags=["Disputes"])


# Raise dispute
@router.post("/", response_model=DisputeResponse)
def raise_dispute(
    dispute: DisputeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    milestone = get_milestone_by_id(db, dispute.milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    return create_dispute(
        db,
        milestone_id=dispute.milestone_id,
        user_id=current_user.id,
        reason=dispute.reason
    )


# Get disputes for milestone
@router.get("/{milestone_id}", response_model=List[DisputeResponse])
def get_milestone_disputes(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return get_disputes_by_milestone(db, milestone_id)


# Resolve dispute (Admin only)
@router.put("/{dispute_id}/resolve", response_model=DisputeResponse)
def resolve_dispute_api(
    dispute_id: int,
    resolution_note: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can resolve disputes")

    return resolve_dispute(db, dispute_id, resolution_note)
