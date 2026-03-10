from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.transaction import Transaction
from app.models.milestone import Milestone
from app.models.project import Project
from app.models.wallet import Wallet
from app.models.wallet_ledger import WalletLedger, LedgerEntryType
from app.core.logger import logger

def release_payment_service(db: Session, milestone_id: int):
    """
    Business logic for processing the escrow release for a milestone.
    Validates milestone status, creates a transaction, and updates payment state.
    """
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()

    if not milestone:
        return None

    if milestone.status.value != "approved":
        return None

    project = db.query(Project).filter(Project.id == milestone.project_id).first()

    if not project or not project.freelancer_id:
        return None

    client_wallet = db.query(Wallet).filter(Wallet.clerk_id == project.client_id).first()
    if not client_wallet or client_wallet.balance < milestone.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds in client wallet to release escrow")

    # Wallet logic step 2: Get freelancer wallet
    freelancer_wallet = db.query(Wallet).filter(Wallet.clerk_id == project.freelancer_id).first()
    if not freelancer_wallet:
        freelancer_wallet = Wallet(clerk_id=project.freelancer_id)
        db.add(freelancer_wallet)
        db.flush()

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
    db.flush() # Flush to get transaction.id

    # Create Ledger Entry for Client (Debit)
    client_wallet.balance -= milestone.amount
    client_ledger = WalletLedger(
        wallet_id=client_wallet.id,
        amount=-milestone.amount,
        entry_type=LedgerEntryType.escrow_release,
        description=f"Released payment for milestone {milestone.id}",
        transaction_id=transaction.id
    )
    db.add(client_ledger)

    # Create Ledger Entry for Freelancer (Credit)
    freelancer_wallet.balance += milestone.amount
    freelancer_ledger = WalletLedger(
        wallet_id=freelancer_wallet.id,
        amount=milestone.amount,
        entry_type=LedgerEntryType.escrow_release,
        description=f"Received payment for milestone {milestone.id}",
        transaction_id=transaction.id
    )
    db.add(freelancer_ledger)

    db.commit()
    db.refresh(transaction)

    logger.info(
        "transaction_completed",
        transaction_id=transaction.id,
        milestone_id=milestone.id,
        amount=milestone.amount,
        payer_id=project.client_id,
        receiver_id=project.freelancer_id
    )

    return transaction
