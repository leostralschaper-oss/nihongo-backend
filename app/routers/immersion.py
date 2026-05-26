# nihongo_backend/app/routers/immersion.py
import os
from fastapi import APIRouter, Depends, Query
from supabase import create_client

from app.middleware.auth import optional_user

router = APIRouter()


def _get_supabase():
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )


@router.get("/content")
async def list_content(
    category: str = Query(default="all"),
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0),
    user=Depends(optional_user),
):
    """List immersion content, optionally filtered by category."""
    db = _get_supabase()

    query = (
        db.table("immersion_content")
        .select("id, category, title, title_ja, image_url, difficulty, vocab_ids, published_at")
        .order("published_at", desc=True)
        .range(offset, offset + limit - 1)
    )

    if category != "all":
        query = query.eq("category", category)

    result = query.execute()
    return result.data


@router.get("/content/{content_id}")
async def get_content(content_id: str, user=Depends(optional_user)):
    """Get full immersion content with segments."""
    db = _get_supabase()

    content = (
        db.table("immersion_content")
        .select("*")
        .eq("id", content_id)
        .single()
        .execute()
    )

    segments = (
        db.table("immersion_segments")
        .select("*")
        .eq("content_id", content_id)
        .order("index")
        .execute()
    )

    return {**content.data, "segments": segments.data}
