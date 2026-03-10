from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.wallet import Wallet
from app.models.wallet_ledger import WalletLedger, LedgerEntryType
from app.core.logger import logger
from app.services.notification_service import send_notification

def get_wallet_balance_service(db: Session, clerk_id: str):
    """Business logic for retrieving a user's wallet balance."""
    wallet = db.query(Wallet).filter(Wallet.clerk_id == clerk_id).first()
    if not wallet:
        wallet = Wallet(clerk_id=clerk_id)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

def deposit_funds_service(db: Session, clerk_id: str, amount: float):
    """Business logic for simulating a deposit into the user's wallet."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive")

    wallet = db.query(Wallet).filter(Wallet.clerk_id == clerk_id).first()
    if not wallet:
        wallet = Wallet(clerk_id=clerk_id)
        db.add(wallet)
        db.flush()

    # Increase balance
    wallet.balance += amount
    
    # Create ledger entry
    ledger_entry = WalletLedger(
        wallet_id=wallet.id,
        amount=amount,
        entry_type=LedgerEntryType.deposit,
        description="User deposit"
    )
    
    db.add(ledger_entry)
    db.commit()
    db.refresh(wallet)
    
    return wallet

def withdraw_funds_service(db: Session, clerk_id: str, amount: float):
    """Business logic for simulating a withdrawal from the user's wallet."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive")

    wallet = db.query(Wallet).filter(Wallet.clerk_id == clerk_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient funds for withdrawal")

    # Decrease balance
    wallet.balance -= amount
    
    # Create ledger entry
    ledger_entry = WalletLedger(
        wallet_id=wallet.id,
        amount=-amount,
        entry_type=LedgerEntryType.withdrawal,
        description="User requested withdrawal"
    )
    
    db.add(ledger_entry)
    db.commit()
    db.refresh(wallet)

    logger.info("withdrawal_processed", clerk_id=clerk_id, amount=amount)
    
    send_notification(clerk_id, "Withdrawal Processed", f"Your withdrawal of {amount} was processed successfully.")

    # STEP 3 Pre-Req: Log suspicious large withdrawals
    if amount >= 10000:
        logger.warning("fraud_flag_large_withdrawal", clerk_id=clerk_id, amount=amount, message="Suspiciously large withdrawal detected")

    return wallet

def get_wallet_ledger_service(db: Session, clerk_id: str, skip: int = 0, limit: int = 100):
    """Business logic to fetch user's wallet ledger."""
    wallet = db.query(Wallet).filter(Wallet.clerk_id == clerk_id).first()
    if not wallet:
        wallet = Wallet(clerk_id=clerk_id)
        db.add(wallet)
        db.commit()
        return []

    ledger = db.query(WalletLedger).filter(WalletLedger.wallet_id == wallet.id).order_by(WalletLedger.created_at.desc()).offset(skip).limit(limit).all()
    return ledger
