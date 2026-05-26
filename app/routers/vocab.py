# nihongo_backend/app/routers/vocab.py
import os
import json
from datetime import datetime, timedelta
import math

import anthropic
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from supabase import create_client, Client

from app.middleware.auth import get_current_user

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

router = APIRouter()


def _get_supabase() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],  # service key for server-side writes
    )


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ReviewSubmission(BaseModel):
    card_id: str
    quality: int  # 0-5 (SM-2 quality rating)


class AddVocabCard(BaseModel):
    word: str
    reading: str
    meaning: str
    example_sentence: str | None = None
    example_reading: str | None = None
    example_translation: str | None = None
    jlpt_level: str | None = None
    tags: list[str] = []


# ---------------------------------------------------------------------------
# SM-2 Algorithm
# ---------------------------------------------------------------------------
def sm2_update(
    repetitions: int,
    interval_days: int,
    ease_factor: float,
    quality: int,
) -> tuple[int, float, int, datetime]:
    """
    Returns (new_interval_days, new_ease_factor, new_repetitions, next_review_at)
    quality: 0-5
      5 = perfect response
      4 = correct with slight hesitation
      3 = correct with serious difficulty
      2 = incorrect, easy to recall
      1 = incorrect, remembered on seeing answer
      0 = complete blackout
    """
    if quality < 3:
        # Failed: restart
        new_repetitions = 0
        new_interval = 1
        new_ef = max(ease_factor - 0.2, 1.3)
    else:
        new_ef = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ef = max(1.3, min(2.5, new_ef))

        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * new_ef)

        new_repetitions = repetitions + 1

    next_review = datetime.utcnow() + timedelta(days=new_interval)
    return new_interval, new_ef, new_repetitions, next_review


def calculate_memory_strength(days_since_review: int, stability: float) -> float:
    """Ebbinghaus forgetting curve: R = e^(-t/S)"""
    if days_since_review <= 0:
        return 1.0
    return math.exp(-days_since_review / max(stability, 1.0))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@router.post("/review")
async def submit_review(
    submission: ReviewSubmission,
    user=Depends(get_current_user),
):
    """Submit an SRS review result for a vocab card."""
    db = _get_supabase()
    user_id = user["sub"]

    # Fetch current card state
    result = (
        db.table("vocab_cards")
        .select("*")
        .eq("id", submission.card_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Vocab card not found")

    card = result.data
    quality = max(0, min(5, submission.quality))

    new_interval, new_ef, new_reps, next_review = sm2_update(
        repetitions=card.get("repetitions", 0),
        interval_days=card.get("interval_days", 1),
        ease_factor=card.get("ease_factor", 2.5),
        quality=quality,
    )

    days_since = (datetime.utcnow() - datetime.fromisoformat(
        card["last_reviewed_at"] or card["learned_at"] or datetime.utcnow().isoformat()
    )).days if card.get("last_reviewed_at") else 0

    memory_strength = calculate_memory_strength(days_since, new_interval)

    # Update card
    db.table("vocab_cards").update({
        "repetitions": new_reps,
        "interval_days": new_interval,
        "ease_factor": new_ef,
        "memory_strength": memory_strength,
        "next_review_at": next_review.isoformat(),
        "last_reviewed_at": datetime.utcnow().isoformat(),
    }).eq("id", submission.card_id).eq("user_id", user_id).execute()

    # Log the review event
    db.table("review_logs").insert({
        "user_id": user_id,
        "card_id": submission.card_id,
        "quality": quality,
        "interval_days": new_interval,
        "ease_factor": new_ef,
        "reviewed_at": datetime.utcnow().isoformat(),
    }).execute()

    # Award XP based on quality
    xp_gained = {5: 20, 4: 15, 3: 10}.get(quality, 0)
    new_level = 1
    new_total_xp = 0
    if xp_gained > 0:
        profile = db.table("profiles").select("total_xp, level") \
            .eq("id", user_id).single().execute()
        if profile.data:
            current_xp = profile.data.get("total_xp", 0) or 0
            new_total_xp = current_xp + xp_gained
            new_level = max(1, new_total_xp // 100 + 1)
            db.table("profiles").update({
                "total_xp": new_total_xp,
                "level": new_level,
                "last_active_at": datetime.utcnow().isoformat(),
            }).eq("id", user_id).execute()

    return {
        "card_id": submission.card_id,
        "new_interval_days": new_interval,
        "new_ease_factor": round(new_ef, 3),
        "next_review_at": next_review.isoformat(),
        "memory_strength": round(memory_strength, 3),
        "xp_gained": xp_gained,
        "total_xp": new_total_xp,
        "level": new_level,
    }


@router.post("/add")
async def add_vocab_card(
    card: AddVocabCard,
    user=Depends(get_current_user),
):
    """Add a new vocabulary card to the user's deck."""
    db = _get_supabase()
    user_id = user["sub"]

    # Check for duplicate
    existing = (
        db.table("vocab_cards")
        .select("id")
        .eq("user_id", user_id)
        .eq("word", card.word)
        .execute()
    )
    if existing.data:
        raise HTTPException(status_code=409, detail="Word already in your vocabulary")

    now = datetime.utcnow().isoformat()
    result = db.table("vocab_cards").insert({
        "user_id": user_id,
        "word": card.word,
        "reading": card.reading,
        "meaning": card.meaning,
        "example_sentence": card.example_sentence,
        "example_reading": card.example_reading,
        "example_translation": card.example_translation,
        "jlpt_level": card.jlpt_level,
        "tags": card.tags,
        "repetitions": 0,
        "interval_days": 1,
        "ease_factor": 2.5,
        "memory_strength": 1.0,
        "next_review_at": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "learned_at": now,
        "last_reviewed_at": now,
    }).execute()

    return {"id": result.data[0]["id"], "word": card.word}


@router.get("/due")
async def get_due_reviews(
    limit: int = 20,
    user=Depends(get_current_user),
):
    """Get cards due for review today."""
    db = _get_supabase()
    user_id = user["sub"]
    now = datetime.utcnow().isoformat()

    result = (
        db.table("vocab_cards")
        .select("*")
        .eq("user_id", user_id)
        .lte("next_review_at", now)
        .order("next_review_at")
        .limit(limit)
        .execute()
    )

    return result.data


class ExplainRequest(BaseModel):
    card_id: str
    mastery_points: int = 0  # 0-3 controls explanation complexity


class MasteryUpdate(BaseModel):
    card_id: str
    all_correct: bool  # True = all tasks correct this session, False = any task wrong


@router.post("/mastery")
async def update_mastery(
    update: MasteryUpdate,
    user=Depends(get_current_user),
):
    """Update mastery points after a completed review session.
    All correct → +1 mastery (max 3). Any wrong → -1 mastery (min 0).
    At 3 mastery points the word is marked as learned.
    """
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("vocab_cards")
        .select("mastery_points")
        .eq("id", update.card_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")

    current = result.data.get("mastery_points") or 0
    new_mastery = min(3, current + 1) if update.all_correct else max(0, current - 1)
    is_learned = new_mastery >= 3

    db.table("vocab_cards").update({
        "mastery_points": new_mastery,
        "is_learned": is_learned,
    }).eq("id", update.card_id).eq("user_id", user_id).execute()

    return {"mastery_points": new_mastery, "is_learned": is_learned}


@router.get("/list")
async def list_vocab(
    limit: int = 100,
    offset: int = 0,
    user=Depends(get_current_user),
):
    """List all vocab cards for the user."""
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("vocab_cards")
        .select("*")
        .eq("user_id", user_id)
        .order("learned_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )

    return {
        "cards": result.data,
        "count": len(result.data),
    }


@router.post("/explain")
async def explain_vocab(
    request: ExplainRequest,
    user=Depends(get_current_user),
):
    """Ask Ollama to explain a vocab word with context-appropriate examples."""
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("vocab_cards")
        .select("word, reading, meaning, example_sentence, example_reading, example_translation")
        .eq("id", request.card_id)
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Card not found")

    card = result.data
    word = card["word"]
    reading = card["reading"]
    meaning = card["meaning"]

    level_desc = {
        0: "sehr einfaches N5-Niveau (nur Grundvokabular, einfachste Grammatik)",
        1: "einfaches N5-N4-Niveau (kurze Sätze, bekannte Partikel)",
        2: "mittleres N4-N3-Niveau (komplexere Strukturen, Verbformen)",
        3: "fortgeschrittenes N3-N2-Niveau (natürliche Sätze, Idiome möglich)",
    }.get(request.mastery_points, "einfaches N5-Niveau")

    example_hint = ""
    if card.get("example_sentence"):
        example_hint = f"\nVorhandenes Beispiel: {card['example_sentence']} ({card.get('example_reading','')}) — {card.get('example_translation','')}"

    prompt = f"""Du bist ein japanischer Sprachlehrer. Erkläre das Wort „{word}" (Lesung: {reading}, Bedeutung: {meaning}) auf {level_desc} für einen deutschsprachigen Lernenden.{example_hint}

Gib folgendes aus:
1. Kurze Erklärung wann/wie man das Wort benutzt (auf Deutsch, 1-2 Sätze)
2. {2 + request.mastery_points} Beispielsätze vom Einfachen zum Schwierigeren, jeder mit:
   - Japanisch (Kana/Kanji)
   - Romaji
   - Deutsche Übersetzung

Formatiere jeden Beispielsatz so:
🇯🇵 [japanischer Satz]
📖 [romaji]
🇩🇪 [deutsche Übersetzung]

Halte es prägnant und praxisnah."""

    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        explanation = msg.content[0].text.strip()
        if explanation:
            return {"explanation": explanation, "word": word}
    except Exception:
        pass

    # Fallback static explanation
    examples = [
        f"🇯🇵 {word}を見ます。\n📖 {reading} wo mimasu.\n🇩🇪 Ich sehe {meaning}.",
        f"🇯🇵 これは{word}です。\n📖 Kore wa {reading} desu.\n🇩🇪 Das ist {meaning}.",
    ]
    fallback = (
        f'**{word}**　({reading})　Bedeutung: {meaning}\n\n'
        "**Verwendung:** Dieses Wort wird im alltaeglichen Japanisch haeufig genutzt.\n\n"
        + "\n\n".join(examples[:1 + request.mastery_points])
    )
    return {"explanation": fallback, "word": word}


@router.get("/puzzle")
async def get_sentence_puzzle(
    user=Depends(get_current_user),
):
    """Generate a sentence puzzle using the user's recently learned vocabulary."""
    db = _get_supabase()
    user_id = user["sub"]

    result = (
        db.table("vocab_cards")
        .select("word, reading, meaning")
        .eq("user_id", user_id)
        .order("learned_at", desc=True)
        .limit(20)
        .execute()
    )

    cards = result.data or []

    # Build a short fallback in case Ollama fails or there's too little vocab
    def _fallback():
        if not cards:
            return {
                "sentence_ja": "これはペンです。",
                "sentence_reading": "kore wa pen desu.",
                "sentence_de": "Das ist ein Stift.",
                "words": ["これ", "は", "ペン", "です。"],
            }
        w = cards[0]
        return {
            "sentence_ja": f"{w['word']}が好きです。",
            "sentence_reading": f"{w['reading']} ga suki desu.",
            "sentence_de": f"Ich mag {w['meaning']}.",
            "words": [w["word"], "が", "好き", "です。"],
        }

    if len(cards) < 2:
        return _fallback()

    vocab_list = "、".join(
        [f"{c['word']}（{c['meaning']}）" for c in cards[:8]]
    )

    prompt = f"""Du bist ein japanischer Sprachlehrer. Der Schüler hat diese Wörter gelernt: {vocab_list}

Erstelle EINEN einfachen japanischen Satz (maximal 7 Wörter/Partikel), der mindestens 2 dieser Vokabeln verwendet.

Antworte NUR mit diesem JSON (kein Text davor oder danach):
{{
  "sentence_ja": "日本語の文。",
  "sentence_reading": "romaji reading.",
  "sentence_de": "Deutsche Übersetzung.",
  "words": ["Wort1", "Partikel", "Wort2", "Wort3", "。"]
}}

Das words-Array enthält den Satz in einzelne Wörter/Partikel aufgeteilt in der RICHTIGEN Reihenfolge. Halte es grammatikalisch korrekt und einfach."""

    try:
        client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        msg = await client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        text = msg.content[0].text
        start = text.find("{")
        end = text.rfind("}") + 1
        if 0 <= start < end:
            data = json.loads(text[start:end])
            if all(k in data for k in ("sentence_ja", "sentence_reading", "sentence_de", "words")):
                return data
    except Exception:
        pass

    return _fallback()
