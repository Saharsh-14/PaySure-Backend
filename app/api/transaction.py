from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import get_current_user
from app.crud.transaction import get_transactions_by_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[dict])
def get_my_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_transactions_by_user(db, current_user.id, skip=skip, limit=limit)
