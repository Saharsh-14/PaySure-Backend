from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from datetime import datetime

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)

    payer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    amount = Column(Float, nullable=False)

    status = Column(String, default="pending")
    # pending / completed / failed / refunded

    transaction_type = Column(String, nullable=False)
    # deposit / release / refund

    created_at = Column(DateTime, default=datetime.utcnow)
