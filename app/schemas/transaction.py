from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from app.models.transaction import TransactionStatus, TransactionType


class TransactionBase(BaseModel):
    milestone_id: int
    payer_id: str
    receiver_id: str
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    transaction_type: TransactionType


class TransactionCreate(TransactionBase):
    status: TransactionStatus = TransactionStatus.LOCKED


class TransactionResponse(TransactionBase):
    id: int
    status: TransactionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
