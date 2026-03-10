from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base

class LedgerEntryType(str, enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    escrow_hold = "escrow_hold"
    escrow_release = "escrow_release"
    refund = "refund"

class WalletLedger(Base):
    __tablename__ = "wallet_ledger"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Positive for credit, negative for debit
    entry_type = Column(Enum(LedgerEntryType), nullable=False)
    description = Column(String, nullable=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    wallet = relationship("Wallet", back_populates="ledger_entries")
    transaction = relationship("Transaction")
