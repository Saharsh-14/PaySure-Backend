from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.disputes import Dispute
from app.models.user import User
from app.models.wallet import Wallet

def get_all_transactions_service(db: Session, skip: int = 0, limit: int = 100):
    """Business logic for an admin to fetch all transactions across the platform."""
    return db.query(Transaction).order_by(Transaction.created_at.desc()).offset(skip).limit(limit).all()

def get_all_disputes_service(db: Session, skip: int = 0, limit: int = 100):
    """Business logic for an admin to fetch all disputes across the platform."""
    return db.query(Dispute).order_by(Dispute.created_at.desc()).offset(skip).limit(limit).all()

def get_all_users_service(db: Session, skip: int = 0, limit: int = 100):
    """Business logic for an admin to fetch all users."""
    return db.query(User).order_by(User.id.asc()).offset(skip).limit(limit).all()

def get_all_wallets_service(db: Session, skip: int = 0, limit: int = 100):
    """Business logic for an admin to fetch all internal wallets and balances."""
    return db.query(Wallet).order_by(Wallet.id.asc()).offset(skip).limit(limit).all()
