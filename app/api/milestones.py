from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.milestone import MilestoneCreate, MilestoneResponse
from app.services.milestone_service import (
    create_milestone_service,
    mark_milestone_completed_service,
    approve_milestone_service
)
from app.api.deps import get_current_user, RoleChecker

router = APIRouter(prefix="/milestones", tags=["Milestones"])


# ---------------------------
# CREATE MILESTONE (Client Only)
# ---------------------------
@router.post("/", response_model=MilestoneResponse)
def create_new_milestone(
    milestone: MilestoneCreate,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["Client"]))
):
    return create_milestone_service(db, milestone, current_user)


# ---------------------------
# GET MILESTONES BY PROJECT
# ---------------------------
@router.get("/{project_id}", response_model=List[MilestoneResponse])
def get_project_milestones(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # This service was previously removed in refactor, I should re-add or call CRUD
    from app.crud.milestone import get_milestones_by_project
    return get_milestones_by_project(db, project_id, skip=skip, limit=limit)


# ---------------------------
# MARK MILESTONE COMPLETED (Freelancer)
# ---------------------------
@router.put("/{milestone_id}/complete", response_model=MilestoneResponse)
def mark_completed(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["Freelancer"]))
):
    return mark_milestone_completed_service(db, milestone_id, current_user)


# ---------------------------
# APPROVE MILESTONE (Client)
# ---------------------------
@router.put("/{milestone_id}/approve", response_model=MilestoneResponse)
def approve_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["Client"]))
):
    return approve_milestone_service(db, milestone_id, current_user)

