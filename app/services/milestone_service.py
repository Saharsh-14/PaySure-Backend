from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud.milestone import (
    create_milestone,
    get_milestones_by_project,
    get_milestone_by_id,
    update_milestone_status
)
from app.crud.project import get_project_by_id
from app.schemas.milestone import MilestoneCreate
from app.services.payment_service import release_payment_service
from app.services.notification_service import send_notification

def create_milestone_service(db: Session, milestone: MilestoneCreate, current_user):
    """Business logic for creating a new milestone."""
    project = get_project_by_id(db, milestone.project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Create the milestone
    new_milestone = create_milestone(
        db,
        title=milestone.title,
        description=milestone.description,
        amount=milestone.amount,
        project_id=milestone.project_id
    )

    send_notification(project.freelancer_id, "New Milestone", f"A new milestone '{milestone.title}' was created.")
    
    return new_milestone

def get_project_milestones_service(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    """Business logic for retrieving milestones of a project."""
    return get_milestones_by_project(db, project_id, skip=skip, limit=limit)

def mark_milestone_completed_service(db: Session, milestone_id: int, current_user):
    """Business logic for a freelancer marking a milestone as completed."""
    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = get_project_by_id(db, milestone.project_id)

    if project.freelancer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    send_notification(project.client_id, "Milestone Completed", f"Freelancer completed milestone #{milestone_id}")

    return update_milestone_status(db, milestone_id, "completed")

def approve_milestone_service(db: Session, milestone_id: int, current_user):
    """Business logic for a client approving a milestone."""
    milestone = get_milestone_by_id(db, milestone_id)

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    project = get_project_by_id(db, milestone.project_id)

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Step 1: Mark milestone approved
    update_milestone_status(db, milestone_id, "approved")

    # Step 2: Release payment (escrow logic)
    release_payment_service(db, milestone_id)

    # Step 3: Notify Freelancer
    project = get_project_by_id(db, milestone.project_id)
    send_notification(project.freelancer_id, "Milestone Approved", f"Milestone #{milestone.id} approved. Funds released.")

    # Step 4: Return updated milestone
    return get_milestone_by_id(db, milestone_id)
