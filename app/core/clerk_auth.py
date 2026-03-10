import urllib.request
import json
import jwt
from fastapi import HTTPException, status
from pprint import pprint

# Ideally, CLERK_JWKS_URL or CLERK_FRONTEND_API is loaded from settings/env.
# For example: https://clerk.example.com/.well-known/jwks.json
# Wait, Clerk JWKS format is typically: https://api.clerk.dev/v1/jwks
# But often the frontend API is used: https://[your-clerk-frontend-api]/.well-known/jwks.json
# We'll use a placeholder URL and standard PyJWT jwks_client.

from app.core.config import settings
# Adding CLERK_JWKS_URL to config would be best, but we can default or dynamically use it.
# Let's construct JWKS_URL from a theoretical CLERK_FRONTEND_API environment variable, or use a dummy for now.
# Actually, PyJWT provides a PyJWKClient to handle fetching and caching JWKS.

clerk_jwks_url = getattr(settings, "CLERK_JWKS_URL", "https://api.clerk.dev/v1/jwks")
jwks_client = jwt.PyJWKClient(clerk_jwks_url)

def verify_clerk_token(token: str) -> dict:
    """
    Verifies the incoming Clerk JWT token against Clerk's JWKS.
    Returns the decoded token payload on success.
    """
    try:
        # Get the unverified header to extract the key ID ('kid')
        unverified_header = jwt.get_unverified_header(token)
        
        # Fetch the signing key from Clerk's JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            # In a real app, verify 'aud' (audience) and 'iss' (issuer) here too.
            options={"verify_aud": False, "verify_iss": False}
        )
        return payload

    except jwt.PyJWKClientError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to fetch signing keys from Clerk",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clerk token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Clerk token",
            headers={"WWW-Authenticate": "Bearer"},
        )
