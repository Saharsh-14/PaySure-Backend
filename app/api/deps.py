from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.clerk_auth import verify_clerk_token
from typing import List

# Bearer token requirement (Clerk tokens are passed this way)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")

class CurrentUser:
    def __init__(self, clerk_id: str, email: str, role: str):
        self.clerk_id = clerk_id
        self.id = clerk_id  # Mapping for backward compatibility
        self.email = email
        self.role = role

def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """
    Verifies the Clerk JWT from the Authorization header.
    Extracts role from public_metadata.
    """
    payload = verify_clerk_token(token)
    
    clerk_id = payload.get("sub")
    if not clerk_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    # Extract role from Clerk public_metadata
    metadata = payload.get("public_metadata", {})
    email = payload.get("email") 
    role = metadata.get("role", "Client") # Default to Client if missing in JWT

    return CurrentUser(clerk_id=clerk_id, email=email, role=role)

def get_current_active_role(current_user: CurrentUser = Depends(get_current_user)) -> str:
    """
    Simple dependency to get the current user's role.
    """
    return current_user.role

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            logger.warning("unauthorized_role_access", user_id=current_user.clerk_id, role=current_user.role, allowed=self.allowed_roles)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user

# Usage example: @router.get("/admin", dependencies=[Depends(RoleChecker(["Admin"]))])
from app.core.logger import logger # Import here to avoid circular dependency if needed, though StructuredLogger is in core.
