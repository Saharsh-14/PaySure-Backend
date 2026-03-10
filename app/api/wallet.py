from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.wallet import WalletResponse, WalletDepositRequest, WalletWithdrawRequest, WalletLedgerResponse
from app.services.wallet_service import (
    get_wallet_balance_service,
    deposit_funds_service,
    withdraw_funds_service,
    get_wallet_ledger_service
)

router = APIRouter(prefix="/wallet", tags=["Wallet"])

@router.get("/balance", response_model=WalletResponse, summary="Get Wallet Balance", description="Retrieves the current authenticated user's digital wallet balance.")
def get_balance(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Fetch the wallet associated with the current user.
    """
    return get_wallet_balance_service(db, current_user.id)

@router.post("/deposit", response_model=WalletResponse, summary="Deposit Funds", description="Simulates a deposit into the user's wallet. Increases balance and records a ledger entry.")
def deposit_funds(
    request: WalletDepositRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Adds positive funds to the wallet and logs a credit item in the ledger.
    """
    return deposit_funds_service(db, current_user.id, request.amount)

@router.post("/withdraw", response_model=WalletResponse, summary="Withdraw Funds", description="Simulates a withdrawal from the user's wallet. Decreases balance if sufficient funds exist.")
def withdraw_funds(
    request: WalletWithdrawRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Reduces the balance of the wallet by the requested amount, performing a balance check first to prevent overdrafts. Logs a debit entry.
    """
    return withdraw_funds_service(db, current_user.id, request.amount)

@router.get("/ledger", response_model=List[WalletLedgerResponse], summary="Get Wallet Ledger", description="Retrieves a paginated list of all financial transactions matching the user's wallet.")
def get_ledger(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Returns an array of deposit, withdrawal, and escrow transfer records.
    """
    return get_wallet_ledger_service(db, current_user.id, skip=skip, limit=limit)
