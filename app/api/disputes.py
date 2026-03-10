from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.schemas.disputes import DisputeCreate, DisputeResponse
from app.services.dispute_service import (
    raise_dispute_service,
    get_milestone_disputes_service,
    resolve_dispute_api_service
)

router = APIRouter(prefix="/disputes", tags=["Disputes"])


# Raise dispute
@router.post("/", response_model=DisputeResponse)
def raise_dispute(
    dispute: DisputeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return raise_dispute_service(db, dispute, current_user)


# Get disputes for milestone
@router.get("/{milestone_id}", response_model=List[DisputeResponse])
def get_milestone_disputes(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_milestone_disputes_service(db, milestone_id)


# Resolve dispute (Admin only)
@router.put("/{dispute_id}/resolve", response_model=DisputeResponse)
def resolve_dispute_api(
    dispute_id: int,
    resolution_note: str,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin"]))
):
    return resolve_dispute_api_service(db, dispute_id, resolution_note, current_user)
