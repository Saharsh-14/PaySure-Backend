from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.milestone import Milestone
from app.models.project import Project


def release_payment(db: Session, milestone_id: int):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()

    if not milestone:
        return None

    if milestone.status != "approved":
        return None

    project = db.query(Project).filter(Project.id == milestone.project_id).first()

    if not project or not project.freelancer_id:
        return None

    # Create transaction record
    transaction = Transaction(
        milestone_id=milestone.id,
        payer_id=project.client_id,
        receiver_id=project.freelancer_id,
        amount=milestone.amount,
        status="completed",
        transaction_type="release"
    )

    db.add(transaction)

    # Optionally update milestone status further
    milestone.status = "paid"

    db.commit()
    db.refresh(transaction)

    return transaction
