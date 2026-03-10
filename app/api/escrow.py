from fastapi import APIRouter

router = APIRouter(prefix="/escrow", tags=["Escrow"])

# Escrow operations are largely handled automatically by milestone approvals.
# Future explicit escrow endpoints (like manual refund controls) would be placed here.
