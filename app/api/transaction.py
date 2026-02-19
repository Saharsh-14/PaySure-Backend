from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.transaction import Transaction

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[dict])
def get_my_transactions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    transactions = db.query(Transaction).filter(
        (Transaction.payer_id == current_user.id) |
        (Transaction.receiver_id == current_user.id)
    ).all()

    return transactions
