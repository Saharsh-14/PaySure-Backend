from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud.milestone import (
    create_milestone,
    get_milestones_by_project,
    get_milestone_by_id,
    update_milestone_status
)
from app.crud.project import get_project_by_id
from app.schemas.milestone import MilestoneCreate
from app.services.escrow_service import release_funds
from app.services.notification_service import send_notification
from app.models.milestone import MilestoneStatus
from app.core.logger import logger

def create_milestone_service(db: Session, milestone: MilestoneCreate, current_user):
    """Business logic for creating a new milestone."""
    project = get_project_by_id(db, milestone.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.client_id != current_user.clerk_id:
        raise HTTPException(status_code=403, detail="Only the project client can create milestones")

    # Create the milestone
    new_milestone = create_milestone(
        db,
        title=milestone.title,
        description=milestone.description,
        amount=milestone.amount,
        project_id=milestone.project_id,
        last_updated_by=current_user.clerk_id
    )

    send_notification(project.freelancer_id, "New Milestone", f"A new milestone '{milestone.title}' was created.")
    
    return new_milestone

def mark_milestone_completed_service(db: Session, milestone_id: int, current_user):
    """Business logic for a freelancer marking a milestone as completed."""
    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    if milestone.status != MilestoneStatus.FUNDED:
        raise HTTPException(status_code=400, detail="Milestone must be FUNDED before completing")

    project = get_project_by_id(db, milestone.project_id)

    if project.freelancer_id != current_user.clerk_id:
        raise HTTPException(status_code=403, detail="Only the assigned freelancer can mark progress as COMPLETED")

    milestone = update_milestone_status(db, milestone_id, MilestoneStatus.COMPLETED, updated_by=current_user.clerk_id)
    
    send_notification(project.client_id, "Milestone Completed", f"Freelancer completed milestone #{milestone_id}")

    return milestone

def approve_milestone_service(db: Session, milestone_id: int, current_user):
    """Business logic for a client approving a milestone and releasing funds."""
    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    if milestone.status != MilestoneStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Only COMPLETED milestones can be approved")

    project = get_project_by_id(db, milestone.project_id)

    if project.client_id != current_user.clerk_id:
        raise HTTPException(status_code=403, detail="Only the client can approve milestones and release funds")

    # Atomic fund release logic
    transaction = release_funds(db, milestone_id, updated_by=current_user.clerk_id)
    
    if not transaction:
        raise HTTPException(status_code=500, detail="Fund release failed")

    send_notification(project.freelancer_id, "Milestone Approved", f"Milestone #{milestone.id} approved. Funds released.")

    return get_milestone_by_id(db, milestone_id)

def dispute_milestone_service(db: Session, milestone_id: int, current_user):
    """Freezes milestone and associated funds."""
    milestone = get_milestone_by_id(db, milestone_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = get_project_by_id(db, milestone.project_id)
    if current_user.clerk_id not in [project.client_id, project.freelancer_id]:
         raise HTTPException(status_code=403, detail="Only project participants can dispute milestones")

    milestone = update_milestone_status(db, milestone_id, MilestoneStatus.DISPUTED, updated_by=current_user.clerk_id)
    logger.warning("milestone_disputed", milestone_id=milestone_id, user_id=current_user.clerk_id)
    
    return milestone
