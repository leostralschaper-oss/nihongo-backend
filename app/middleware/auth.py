# nihongo_backend/app/middleware/auth.py
import os
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    """Decode and verify a Supabase JWT."""
    secret = os.environ.get("SUPABASE_JWT_SECRET", "")
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Require authentication — raises 401 if not authenticated."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    return _decode_token(credentials.credentials)


async def optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """Optional authentication — returns None if not authenticated."""
    if credentials is None:
        return None
    try:
        return _decode_token(credentials.credentials)
    except HTTPException:
        return None
