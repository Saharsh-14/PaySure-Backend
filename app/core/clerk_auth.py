import urllib.request
import json
import jwt
from fastapi import HTTPException, status
from app.core.config import settings

def verify_clerk_token(token: str) -> dict:
    """
    Verifies the incoming Clerk JWT token against Clerk's JWKS.
    Returns the decoded token payload on success.
    """
    # Initialize jwks_client with the latest URL from settings
    clerk_jwks_url = settings.CLERK_JWKS_URL
    jwks_client = jwt.PyJWKClient(clerk_jwks_url)
    
    print(f"DEBUG: Verifying token for JWKS: {clerk_jwks_url}", flush=True)
    try:
        # Get the unverified header to extract the key ID ('kid')
        # unverified_header = jwt.get_unverified_header(token) # No longer needed but kept for ref
        
        # Fetch the signing key from Clerk's JWKS
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_aud": False, "verify_iss": False}
        )
        print(f"DEBUG: Token verified successfully for sub: {payload.get('sub')}", flush=True)
        return payload

    except jwt.PyJWKClientError as e:
        print(f"DEBUG: Clerk Auth Error (JWK): {str(e)}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Unable to fetch signing keys from Clerk: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.ExpiredSignatureError:
        print(f"DEBUG: Clerk Auth Error: Token Expired", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clerk token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        print(f"DEBUG: Clerk Auth Error (Invalid): {str(e)}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Clerk token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"DEBUG: Clerk Auth Error (General): {str(e)}", flush=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Auth error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
