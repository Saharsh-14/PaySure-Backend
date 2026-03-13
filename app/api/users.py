from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

class UserLookupResponse(BaseModel):
    clerk_id: str
    email: str
    full_name: Optional[str]
    role: str

@router.get("/lookup", response_model=UserLookupResponse)
def lookup_user_by_email(
    email: str = Query(..., description="The email address to look up"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Look up a user securely by email to fetch their name and role.
    Requires authentication. Includes JIT sync from Clerk if not found locally.
    """
    from app.services.user_service import get_or_sync_user
    user = get_or_sync_user(db, email)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found in PaySure or Clerk")
        
    return UserLookupResponse(
        clerk_id=user.clerk_id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else user.role
    )
@router.get("/me", response_model=UserLookupResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get the current user's profile from the local database.
    This ensures we have their role and other PaySure-specific data.
    """
    # current_user from get_current_user is already the DB user object
    return UserLookupResponse(
        clerk_id=current_user.clerk_id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    )
