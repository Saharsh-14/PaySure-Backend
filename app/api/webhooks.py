from fastapi import APIRouter, Request, HTTPException, Depends, status
from svix.webhooks import Webhook, WebhookVerificationError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.core.logger import logger
import json

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Listens for Clerk webhooks (user.created, user.updated) and syncs to local DB.
    """
    # 1. Get headers for verification
    headers = request.headers
    svix_id = headers.get("svix-id")
    svix_timestamp = headers.get("svix-timestamp")
    svix_signature = headers.get("svix-signature")

    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing svix headers")

    # 2. Get the body
    payload = await request.body()
    
    # 3. Verify the signature
    try:
        wh = Webhook(settings.CLERK_WEBHOOK_SECRET)
        msg = wh.verify(payload, headers)
    except WebhookVerificationError as e:
        logger.error("webhook_verification_failed", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 4. Handle the event
    data = json.loads(payload)
    event_type = data.get("type")
    object_data = data.get("data", {})

    if event_type in ["user.created", "user.updated"]:
        clerk_id = object_data.get("id")
        email_addresses = object_data.get("email_addresses", [])
        email = email_addresses[0].get("email_address") if email_addresses else None
        first_name = object_data.get("first_name", "")
        last_name = object_data.get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        
        # Metadata check for role
        public_metadata = object_data.get("public_metadata", {})
        role_str = public_metadata.get("role")
        
        # Default role logic based on custom signup attribute if role is missing
        if not role_str:
            unsafe_metadata = object_data.get("unsafe_metadata", {})
            role_str = unsafe_metadata.get("role", "Client") # Default to Client if nothing else

        # Map string to Enum (case-insensitive fallback)
        try:
            # Capitalize first letter to match Enum names (Admin, Client, Freelancer)
            if role_str:
                role_str = role_str.capitalize()
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.CLIENT

        # Sync with database
        user = db.query(User).filter(User.clerk_id == clerk_id).first()
        if user:
            user.email = email
            user.full_name = full_name
            user.role = role
            logger.info("user_updated", clerk_id=clerk_id, role=role)
        else:
            new_user = User(
                clerk_id=clerk_id,
                email=email,
                full_name=full_name,
                role=role
            )
            db.add(new_user)
            logger.info("user_created", clerk_id=clerk_id, role=role)
        
        db.commit()

    return {"status": "success"}
