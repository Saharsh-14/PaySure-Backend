from sqlalchemy.orm import Session
from app.models.milestone import Milestone


# Create new milestone
def create_milestone(db: Session, title: str, description: str, amount: float, project_id: int):
    milestone = Milestone(
        title=title,
        description=description,
        amount=amount,
        project_id=project_id,
        status="pending"
    )

    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


# Get milestones by project
def get_milestones_by_project(db: Session, project_id: int):
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()


# Get milestone by ID
def get_milestone_by_id(db: Session, milestone_id: int):
    return db.query(Milestone).filter(Milestone.id == milestone_id).first()


# Update milestone status
def update_milestone_status(db: Session, milestone_id: int, new_status: str):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()

    if milestone:
        milestone.status = new_status
        db.commit()
        db.refresh(milestone)

    return milestone
