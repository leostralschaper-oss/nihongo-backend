# nihongo_backend/app/routers/conversation.py
import json
import os
import time
from collections import defaultdict
from typing import AsyncGenerator

import anthropic
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.middleware.auth import get_current_user

router = APIRouter()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ---------------------------------------------------------------------------
# Simple in-memory rate limiter: max 30 AI requests per user per hour
# ---------------------------------------------------------------------------
_rate_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 30
_RATE_WINDOW = 3600  # seconds


def _check_rate_limit(user_id: str) -> None:
    now = time.time()
    window_start = now - _RATE_WINDOW
    calls = [t for t in _rate_store[user_id] if t > window_start]
    if len(calls) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded: max {_RATE_LIMIT} AI requests per hour.",
        )
    calls.append(now)
    _rate_store[user_id] = calls

# ---------------------------------------------------------------------------
# Personality system prompts
# ---------------------------------------------------------------------------
PERSONALITY_PROMPTS = {
    "friendly_teacher": """You are Yuki, a warm and patient Japanese language teacher.
Your style:
- Correct mistakes gently, always showing the corrected form
- Explain grammar in simple English when needed
- Encourage the student frequently
- Use a mix of Japanese and English appropriate to their level
- When the user makes a grammar mistake, include a "correction" at the end in this format:
  [CORRECTION: original → corrected (brief explanation)]
- Keep responses concise — 2-4 sentences unless a longer explanation is needed""",

    "anime_character": """You are Sakura, an energetic anime-style character who loves teaching Japanese!
Your style:
- Use casual Japanese (plain form, not desu/masu) mixed with English
- Include anime-style expressions like ね, よ, でしょ, わ
- Be enthusiastic and playful — use ! frequently
- Reference Japanese pop culture naturally
- Correct mistakes in a fun, encouraging way
- Keep it casual and exciting""",

    "business_mentor": """You are Tanaka-san, a professional Japanese business mentor.
Your style:
- Focus on keigo (polite/formal Japanese) and business vocabulary
- Use formal です/ます forms consistently
- Provide context for when expressions are appropriate in a business setting
- Correct mistakes professionally, with clear explanations
- Mention cultural context when relevant to business situations
- Be concise and professional""",
}

DIFFICULTY_INSTRUCTIONS = {
    "beginner": """The student is a beginner (JLPT N5/N4 level).
- Use simple vocabulary and short sentences
- Write Japanese in hiragana/katakana with kanji only when absolutely necessary
- Always provide the reading for any kanji used
- Speak mostly in English with Japanese phrases woven in
- Focus on basic grammar patterns""",

    "intermediate": """The student is intermediate (JLPT N3/N2 level).
- Use natural Japanese sentences with common kanji (provide furigana for N1-level kanji)
- Mix Japanese and English naturally — more Japanese as conversations progress
- Introduce more complex grammar patterns
- Expect them to understand basic grammar without full explanations""",

    "advanced": """The student is advanced (JLPT N1 level).
- Use natural, native-level Japanese including idioms and expressions
- Minimal English — respond mostly in Japanese unless explaining nuanced grammar
- Use all kanji without furigana
- Challenge them with complex grammar and nuance
- Point out subtle expression differences""",
}


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------
class ConversationRequest(BaseModel):
    message: str
    history: list[dict]  # [{"role": "user"|"assistant", "content": "..."}]
    personality: str = "friendly_teacher"
    difficulty: str = "beginner"

    model_config = {"str_max_length": 2000}  # cap message at 2000 chars


# ---------------------------------------------------------------------------
# Streaming endpoint
# ---------------------------------------------------------------------------
@router.post("/stream")
async def stream_conversation(
    request: ConversationRequest,
    user=Depends(get_current_user),
):
    """Stream AI conversation responses via SSE."""
    _check_rate_limit(user["sub"])

    personality = request.personality if request.personality in PERSONALITY_PROMPTS \
        else "friendly_teacher"
    difficulty = request.difficulty if request.difficulty in DIFFICULTY_INSTRUCTIONS \
        else "beginner"

    system_prompt = (
        PERSONALITY_PROMPTS[personality]
        + "\n\n"
        + DIFFICULTY_INSTRUCTIONS[difficulty]
        + "\n\nIMPORTANT: Keep responses focused and conversational. "
        "Never write more than 150 words unless the student explicitly asks for a long explanation."
    )

    messages = request.history[-20:] if len(request.history) > 20 else request.history
    messages = [*messages, {"role": "user", "content": request.message}]

    return StreamingResponse(
        _stream_claude(system_prompt, messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


async def _stream_claude(system: str, messages: list) -> AsyncGenerator[str, None]:
    """Yield SSE-formatted chunks from Claude."""
    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    try:
        async with client.messages.stream(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=system,
            messages=messages,
        ) as stream:
            async for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"


# ---------------------------------------------------------------------------
# Non-streaming endpoint (fallback / testing)
# ---------------------------------------------------------------------------
@router.post("/message")
async def single_message(
    request: ConversationRequest,
    user=Depends(get_current_user),
):
    _check_rate_limit(user["sub"])
    personality = request.personality if request.personality in PERSONALITY_PROMPTS \
        else "friendly_teacher"
    difficulty = request.difficulty if request.difficulty in DIFFICULTY_INSTRUCTIONS \
        else "beginner"

    system_prompt = (
        PERSONALITY_PROMPTS[personality]
        + "\n\n"
        + DIFFICULTY_INSTRUCTIONS[difficulty]
    )

    messages = request.history[-20:]
    messages = [*messages, {"role": "user", "content": request.message}]

    client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
    msg = await client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=512,
        system=system_prompt,
        messages=messages,
    )
    return {"content": msg.content[0].text}
