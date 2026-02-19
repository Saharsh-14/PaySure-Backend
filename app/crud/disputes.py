from sqlalchemy.orm import Session
from app.models.disputes import Dispute


def create_dispute(db: Session, milestone_id: int, user_id: int, reason: str):
    dispute = Dispute(
        milestone_id=milestone_id,
        raised_by=user_id,
        reason=reason,
        status="open"
    )

    db.add(dispute)
    db.commit()
    db.refresh(dispute)

    return dispute


def get_disputes_by_milestone(db: Session, milestone_id: int):
    return db.query(Dispute).filter(Dispute.milestone_id == milestone_id).all()


def resolve_dispute(db: Session, dispute_id: int, resolution_note: str):
    dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()

    if dispute:
        dispute.status = "resolved"
        dispute.resolution_note = resolution_note
        db.commit()
        db.refresh(dispute)

    return dispute
