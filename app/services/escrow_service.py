from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionStatus, TransactionType
from app.models.milestone import Milestone, MilestoneStatus
from app.models.project import Project
from app.core.logger import logger

def release_funds(db: Session, milestone_id: int, updated_by: str = None):
    """
    Atomically releases funds for a milestone.
    Updates Milestone status to APPROVED and creates a LOCKED Transaction record.
    """
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()

    if not milestone or milestone.status != MilestoneStatus.COMPLETED:
        return None

    project = db.query(Project).filter(Project.id == milestone.project_id).first()

    if not project or not project.freelancer_id:
        return None

    try:
        # Create transaction record (Defaults to LOCKED status)
        transaction = Transaction(
            milestone_id=milestone.id,
            payer_id=project.client_id,
            receiver_id=project.freelancer_id,
            amount=milestone.amount,
            status=TransactionStatus.LOCKED, # Requirement: defaults to LOCKED
            transaction_type=TransactionType.release
        )

        db.add(transaction)

        # Update milestone status to APPROVED
        milestone.status = MilestoneStatus.APPROVED
        if updated_by:
            milestone.last_updated_by = updated_by

        # Atomic commit
        db.commit()
        db.refresh(transaction)
        
        logger.info("funds_released_locked", milestone_id=milestone.id, transaction_id=transaction.id)
        return transaction

    except Exception as e:
        db.rollback()
        logger.error("fund_release_failed", milestone_id=milestone_id, error=str(e))
        return None
