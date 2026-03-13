from sqlalchemy.orm import Session
from app.models.milestone import Milestone, MilestoneStatus
from decimal import Decimal


# Create new milestone
def create_milestone(db: Session, title: str, description: str, amount: Decimal, project_id: int, last_updated_by: str = None):
    milestone = Milestone(
        title=title,
        description=description,
        amount=amount,
        project_id=project_id,
        status=MilestoneStatus.PENDING,
        last_updated_by=last_updated_by
    )

    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


# Get milestones by project
def get_milestones_by_project(db: Session, project_id: int, skip: int = 0, limit: int = 100):
    return db.query(Milestone).filter(Milestone.project_id == project_id).offset(skip).limit(limit).all()


# Get milestone by ID
def get_milestone_by_id(db: Session, milestone_id: int):
    return db.query(Milestone).filter(Milestone.id == milestone_id).first()


# Update milestone status
def update_milestone_status(db: Session, milestone_id: int, new_status: str, updated_by: str = None):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()

    if milestone:
        milestone.status = new_status
        if updated_by:
            milestone.last_updated_by = updated_by
        db.commit()
        db.refresh(milestone)

    return milestone
