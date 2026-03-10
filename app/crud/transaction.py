from sqlalchemy.orm import Session
from app.models.transaction import Transaction

def get_transactions_by_user(db: Session, clerk_id: str, skip: int = 0, limit: int = 100):
    """Get all transactions where the user is either the payer or the receiver."""
    return db.query(Transaction).filter(
        (Transaction.payer_id == clerk_id) | (Transaction.receiver_id == clerk_id)
    ).offset(skip).limit(limit).all()
