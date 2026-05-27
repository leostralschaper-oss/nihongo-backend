# nihongo_backend/app/middleware/auth.py
import os
import time
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer(auto_error=False)

# Supabase now issues asymmetric JWTs (ES256/RS256) so a local secret-based
# decode is no longer enough. Delegate validation to Supabase's
# /auth/v1/user endpoint — it accepts the bearer token, returns the user
# record on success, 401 otherwise. Avoids pulling cryptography for JWKS.
_SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
# `/auth/v1/user` accepts either anon or service key as the apikey header —
# we fall back to the service key so Railway needs no new env var.
_SUPABASE_ANON_KEY = (
    os.environ.get("SUPABASE_ANON_KEY")
    or os.environ.get("SUPABASE_SERVICE_KEY", "")
)

# Small in-memory cache keyed by token (TTL 5 min) so repeated requests in a
# burst don't all hit Supabase. Tokens themselves are bearer credentials, so
# never log them.
_cache: dict[str, tuple[float, dict]] = {}
_CACHE_TTL = 300


def _decode_token(token: str) -> dict:
    """Validate a Supabase JWT by asking Supabase about it."""
    if not _SUPABASE_URL or not _SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auth not configured (SUPABASE_URL / SUPABASE_ANON_KEY missing)",
        )

    now = time.time()
    cached = _cache.get(token)
    if cached and cached[0] > now:
        return cached[1]

    try:
        r = httpx.get(
            f"{_SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": _SUPABASE_ANON_KEY,
            },
            timeout=10.0,
        )
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth provider unreachable: {e}",
        )

    if r.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    u = r.json()
    user = {
        "sub": u.get("id"),
        "email": u.get("email"),
        "role": u.get("role") or "authenticated",
        "aud": u.get("aud"),
        # keep the raw payload available for downstream callers
        "user_metadata": u.get("user_metadata", {}),
        "app_metadata": u.get("app_metadata", {}),
    }
    _cache[token] = (now + _CACHE_TTL, user)
    # Best-effort cache size cap
    if len(_cache) > 500:
        for k in list(_cache.keys())[:100]:
            _cache.pop(k, None)
    return user


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
