from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User, UserRole
from app.core.config import settings
import urllib.request
import urllib.parse
import json

def get_or_sync_user(db: Session, email: str) -> User:
    """
    Finds a user in the local database by email (case-insensitive).
    If not found, attempts to sync from Clerk API.
    """
    # 1. Search locally
    user = db.query(User).filter(User.email.ilike(email)).first()
    if user:
        return user

    # 2. JIT Sync from Clerk
    try:
        # Revert to standard Clerk API if subdomain not needed, or keep it flexible.
        # Based on curl test, api.clerk.com works fine with standard User-Agent.
        clerk_base = "https://api.clerk.com"
            
        clerk_url = f"{clerk_base}/v1/users?email_address={urllib.parse.quote(email)}"
        req = urllib.request.Request(clerk_url)
        req.add_header("Authorization", f"Bearer {settings.CLERK_SECRET_KEY}")
        req.add_header("User-Agent", "curl/7.68.0")
        
        with urllib.request.urlopen(req) as response:
            clerk_data = json.loads(response.read().decode())
            
            if clerk_data and len(clerk_data) > 0:
                clerk_user = clerk_data[0]
                clerk_id = clerk_user.get("id")
                
                # Fetch basic info
                first_name = clerk_user.get("first_name", "")
                last_name = clerk_user.get("last_name", "")
                full_name = f"{first_name} {last_name}".strip() or email.split('@')[0]
                
                # Get role from metadata
                public_metadata = clerk_user.get("public_metadata", {})
                role_str = public_metadata.get("role")
                
                if not role_str:
                    unsafe_metadata = clerk_user.get("unsafe_metadata", {})
                    role_str = unsafe_metadata.get("role", "Client")
                
                # Map to Enum
                try:
                    role = UserRole(role_str.capitalize() if role_str else "Client")
                except ValueError:
                    role = UserRole.CLIENT
                
                # Check if this clerk_id exists under a different email maybe? 
                # (unlikely but safe to check)
                existing_by_id = db.query(User).filter(User.clerk_id == clerk_id).first()
                if existing_by_id:
                    existing_by_id.email = email.lower()
                    existing_by_id.full_name = full_name
                    existing_by_id.role = role
                    user = existing_by_id
                else:
                    # Final check for email uniqueness to avoid integrity errors
                    existing_by_email = db.query(User).filter(User.email == email.lower()).first()
                    if existing_by_email:
                        # Email exists but with different clerk_id? Overwrite it.
                        db.delete(existing_by_email)
                        db.flush()
                        
                    user = User(
                        clerk_id=clerk_id,
                        email=email.lower(),
                        full_name=full_name,
                        role=role
                    )
                    db.add(user)
                
                db.commit()
                db.refresh(user)
                return user
            else:
                from app.core.logger import logger
                logger.warning("jit_sync_no_user_found", email=email)
    except Exception as e:
        from app.core.logger import logger
        logger.error("jit_sync_failed", email=email, error=str(e))
        db.rollback()

    return None
