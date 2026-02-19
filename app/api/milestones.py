from app.services.escrow_service import release_payment
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.milestone import MilestoneCreate, MilestoneResponse
from app.crud.milestone import (
    create_milestone,
    get_milestones_by_project,
    get_milestone_by_id,
    update_milestone_status
)
from app.crud.project import get_project_by_id
from app.api.deps import get_current_user

router = APIRouter(prefix="/milestones", tags=["Milestones"])


# ---------------------------
# CREATE MILESTONE (Client Only)
# ---------------------------
@router.post("/", response_model=MilestoneResponse)
def create_new_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    project = get_project_by_id(db, milestone.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return create_milestone(
        db,
        title=milestone.title,
        description=milestone.description,
        amount=milestone.amount,
        project_id=milestone.project_id
    )


# ---------------------------
# GET MILESTONES BY PROJECT
# ---------------------------
@router.get("/{project_id}", response_model=List[MilestoneResponse])
def get_project_milestones(
    project_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return get_milestones_by_project(db, project_id)


# ---------------------------
# MARK MILESTONE COMPLETED (Freelancer)
# ---------------------------
@router.put("/{milestone_id}/complete", response_model=MilestoneResponse)
def mark_completed(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = get_project_by_id(db, milestone.project_id)

    if project.freelancer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return update_milestone_status(db, milestone_id, "completed")


# ---------------------------
# APPROVE MILESTONE (Client)
# ---------------------------
@router.put("/{milestone_id}/approve", response_model=MilestoneResponse)
def approve_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = get_project_by_id(db, milestone.project_id)

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Step 1: Mark milestone approved
    update_milestone_status(db, milestone_id, "approved")

    # Step 2: Release payment (escrow logic)
    release_payment(db, milestone_id)

    # Step 3: Return updated milestone
    return get_milestone_by_id(db, milestone_id)

