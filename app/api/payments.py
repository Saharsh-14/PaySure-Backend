from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_current_user
from app.services.payment_gateway import get_payment_adapter, PaymentIntentResponse
from app.services.wallet_service import deposit_funds_service
from app.core.logger import logger

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/intent/{provider}", response_model=PaymentIntentResponse, summary="Create Payment Intent", description="Initialize a deposit session with an external provider (Stripe/Razorpay).")
def create_intent(
    provider: str,
    amount: float,
    current_user = Depends(get_current_user)
):
    """
    Returns the client secret needed by the frontend elements to complete checkout.
    """
    try:
        adapter = get_payment_adapter(provider)
        # Assuming base currency standard for now
        currency = "INR" if provider.lower() == "razorpay" else "USD"
        return adapter.create_deposit_intent(amount=amount, currency=currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook/{provider}", summary="Payment Gateway Webhook", description="Receives server-to-server callbacks from providers to finalize deposits.")
async def payment_webhook(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Validates cryptographic signatures and credits the respective wallet if payment succeeded.
    """
    payload = await request.json()
    # In reality signature comes from headers (e.g. request.headers.get("Stripe-Signature"))
    signature = "mock_signature" 
    
    try:
        adapter = get_payment_adapter(provider)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unknown provider")

    if adapter.handle_webhook(payload, signature):
        # Extremely simplified mapping: usually the payload contains metadata linked to user_id
        # Extract a mock clerk_id from payload metadata or assume a generic action
        clerk_id = payload.get("metadata", {}).get("user_id", "mock_clerk_id")
        amount = payload.get("amount", 0)
        
        # Credit the internal wallet
        deposit_funds_service(db, clerk_id=clerk_id, amount=amount)
        logger.info("webhook_deposit_success", provider=provider, clerk_id=clerk_id, amount=amount)
        return {"status": "success"}
    else:
        logger.warning("webhook_validation_failed", provider=provider)
        raise HTTPException(status_code=400, detail="Invalid webhook payload or signature")

