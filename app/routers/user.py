# nihongo_backend/app/routers/user.py
"""
DSGVO-compliant user account endpoints.

- /export  → Right to data portability (Art. 20 DSGVO)
- /delete  → Right to erasure (Art. 17 DSGVO) + Apple Guideline 5.1.1(v)
"""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import create_client, Client

from app.middleware.auth import get_current_user

router = APIRouter()


def _get_supabase() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )


# ---------------------------------------------------------------------------
# GET /user/export — full data export (JSON)
# ---------------------------------------------------------------------------
@router.get("/export")
async def export_user_data(user=Depends(get_current_user)):
    """Return all personal data of the authenticated user as JSON.
    Fulfils DSGVO Art. 20 (Recht auf Datenübertragbarkeit)."""
    db = _get_supabase()
    user_id = user["sub"]

    def safe_select(table: str, **filters):
        try:
            q = db.table(table).select("*")
            for k, v in filters.items():
                q = q.eq(k, v)
            return q.execute().data or []
        except Exception:
            return []

    profile = safe_select("profiles", id=user_id)
    return {
        "export_format_version": 1,
        "user_id": user_id,
        "email": user.get("email"),
        "profile": profile[0] if profile else None,
        "vocab_cards": safe_select("vocab_cards", user_id=user_id),
        "review_logs": safe_select("review_logs", user_id=user_id),
        "grammar_errors": safe_select("grammar_errors", user_id=user_id),
    }


# ---------------------------------------------------------------------------
# DELETE /user/delete — full account erasure
# ---------------------------------------------------------------------------
@router.delete("/delete")
async def delete_user_account(user=Depends(get_current_user)):
    """Permanently delete the authenticated user's account and all data.

    Fulfils DSGVO Art. 17 (Recht auf Löschung) and Apple Guideline 5.1.1(v).
    All user-data tables CASCADE on auth.users deletion (see schema.sql).
    """
    db = _get_supabase()
    user_id = user["sub"]

    try:
        # Best-effort explicit deletes first (in case any table lacks cascade)
        for table in ("ai_rate_events", "review_logs", "grammar_errors", "vocab_cards", "profiles"):
            try:
                db.table(table).delete().eq("user_id", user_id).execute()
            except Exception:
                try:
                    db.table(table).delete().eq("id", user_id).execute()
                except Exception:
                    pass

        # Delete the auth user — cascades remaining references
        db.auth.admin.delete_user(user_id)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Account deletion failed: {e}",
        )

    return {"deleted": True, "user_id": user_id}
