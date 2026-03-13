from sqlalchemy import Column, Integer, Numeric, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class TransactionStatus(str, enum.Enum):
    LOCKED = "LOCKED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"

class TransactionType(str, enum.Enum):
    deposit = "deposit"
    release = "release"
    refund = "refund"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    payer_id = Column(String, nullable=False, index=True)
    receiver_id = Column(String, nullable=False, index=True)

    amount = Column(Numeric(12, 2), nullable=False)

    status = Column(Enum(TransactionStatus), default=TransactionStatus.LOCKED)

    transaction_type = Column(Enum(TransactionType), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    milestone = relationship("Milestone", back_populates="transactions")
