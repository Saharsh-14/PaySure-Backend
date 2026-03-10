from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WalletLedgerResponse(BaseModel):
    id: int
    amount: float
    entry_type: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class WalletResponse(BaseModel):
    id: int
    clerk_id: str
    balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class WalletDepositRequest(BaseModel):
    amount: float

class WalletWithdrawRequest(BaseModel):
    amount: float
