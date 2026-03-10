from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.clerk_auth import verify_clerk_token

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
    Returns a unified object with clerk_id, role, and email.
    """
    payload = verify_clerk_token(token)
    
    clerk_id = payload.get("sub")
    if not clerk_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    metadata = payload.get("public_metadata", {})
    email = payload.get("email") 
    role = metadata.get("role", "client")

    return CurrentUser(clerk_id=clerk_id, email=email, role=role)

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: CurrentUser = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user
