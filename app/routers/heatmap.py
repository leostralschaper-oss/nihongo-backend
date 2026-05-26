# nihongo_backend/app/routers/heatmap.py
import os
from datetime import datetime
from fastapi import APIRouter, Depends
from supabase import create_client

from app.middleware.auth import get_current_user

router = APIRouter()


def _get_supabase():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )


@router.get("/overview")
async def get_heatmap_overview(user=Depends(get_current_user)):
    """Return memory strength overview for all user vocab."""
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("vocab_cards")
        .select("id, word, reading, meaning, memory_strength, next_review_at, tags, interval_days, last_reviewed_at")
        .eq("user_id", user_id)
        .order("memory_strength")
        .execute()
    )

    cards = result.data
    now = datetime.utcnow()

    # Enrich with due status
    for card in cards:
        if card.get("next_review_at"):
            next_review = datetime.fromisoformat(card["next_review_at"])
            card["is_due"] = next_review <= now
        else:
            card["is_due"] = True

    return {
        "total": len(cards),
        "cards": cards,
        "summary": {
            "strong": sum(1 for c in cards if (c.get("memory_strength") or 0) >= 0.8),
            "medium": sum(1 for c in cards if 0.5 <= (c.get("memory_strength") or 0) < 0.8),
            "weak": sum(1 for c in cards if 0.2 <= (c.get("memory_strength") or 0) < 0.5),
            "forgotten": sum(1 for c in cards if (c.get("memory_strength") or 0) < 0.2),
            "due_today": sum(1 for c in cards if c.get("is_due")),
        },
    }


@router.get("/grammar-errors")
async def get_grammar_errors(user=Depends(get_current_user)):
    """Return aggregated grammar error patterns."""
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("grammar_errors")
        .select("pattern, count")
        .eq("user_id", user_id)
        .order("count", desc=True)
        .limit(20)
        .execute()
    )

    return result.data
