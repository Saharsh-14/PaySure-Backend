from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.api.deps import RoleChecker

# In a real app we'd map to dedicated schemas (like UserResponse), we can use dict/Any or dedicated models
from app.schemas.user import UserResponse
from app.schemas.disputes import DisputeResponse
from app.schemas.wallet import WalletResponse
# Transaction lacks a schema in the provided logs (relies on dict in transaction.py), so we omit strict typing for now or reuse dict
from typing import Any

from app.services.admin_service import (
    get_all_transactions_service,
    get_all_disputes_service,
    get_all_users_service,
    get_all_wallets_service
)

router = APIRouter(prefix="/admin", tags=["Admin"])

admin_dependency = Depends(RoleChecker(["admin"]))

@router.get("/transactions", summary="List All Transactions", description="Admin-only. Retrieves a paginated list of all platform transactions.")
def list_all_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user = admin_dependency
) -> List[Any]:
    return get_all_transactions_service(db, skip=skip, limit=limit)

@router.get("/disputes", response_model=List[DisputeResponse], summary="List All Disputes", description="Admin-only. Retrieves a paginated list of all platform disputes.")
def list_all_disputes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user = admin_dependency
):
    return get_all_disputes_service(db, skip=skip, limit=limit)

@router.get("/users", response_model=List[UserResponse], summary="List All Users", description="Admin-only. Retrieves a paginated list of all platform users.")
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user = admin_dependency
):
    return get_all_users_service(db, skip=skip, limit=limit)

@router.get("/wallets", response_model=List[WalletResponse], summary="List All Wallets", description="Admin-only. Retrieves a paginated list of all internal platform wallets and balances.")
def list_all_wallets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user = admin_dependency
):
    return get_all_wallets_service(db, skip=skip, limit=limit)
