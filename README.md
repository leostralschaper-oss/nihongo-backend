# Nihongo App — Setup Guide

Japanese language learning app: AI conversation + Memory Heatmap + Immersion Mode.

---

## Stack
- **Frontend**: Flutter (iOS + Android)
- **Backend**: Python FastAPI
- **Auth + DB + Storage**: Supabase
- **AI**: Claude (Anthropic API)

---

## Quick Start

### 1. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Go to **SQL Editor** and run `nihongo_backend/schema.sql`
3. Copy your project URL, anon key, service key, and JWT secret

### 2. Backend Setup

```bash
cd nihongo_backend
cp .env.example .env
# Fill in your keys in .env

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Flutter Setup

1. Install Flutter: https://docs.flutter.dev/get-started/install
2. Fill in your keys in `lib/core/constants/app_constants.dart`:
   - `supabaseUrl` — your Supabase project URL
   - `supabaseAnonKey` — your Supabase anon key
   - `apiBaseUrl` — your FastAPI server URL (e.g. `http://localhost:8000`)

```bash
cd nihongo_app
flutter pub get
flutter run
```

### 4. Generate Riverpod/Freezed code

```bash
cd nihongo_app
dart run build_runner build --delete-conflicting-outputs
```

---

## Folder Structure

```
nihongo_app/
  lib/
    core/
      constants/     # App-wide constants (URLs, limits)
      theme/         # Light + dark theme
      router/        # GoRouter navigation
    features/
      auth/          # Login, register, Supabase auth
      conversation/  # AI chat screen + streaming
      heatmap/       # Memory heatmap + SRS
      immersion/     # Content list + sentence reader
      home/          # Dashboard + bottom nav
    shared/
      models/        # Freezed data models
      services/      # Shared services

nihongo_backend/
  app/
    routers/
      conversation.py  # Claude streaming endpoint
      vocab.py         # SRS review submission
      heatmap.py       # Memory overview
      immersion.py     # Content listing
    middleware/
      auth.py          # Supabase JWT verification
  schema.sql           # Full Supabase DB schema
```

---

## Deployment

**Backend**: Deploy to [Railway](https://railway.app) or [Render](https://render.com)
- Set all `.env` variables as environment variables in the dashboard
- Railway auto-detects `requirements.txt` and runs uvicorn

**Flutter**: Build release versions
```bash
flutter build apk --release        # Android
flutter build ipa --release        # iOS (requires Mac + Xcode)
```

---

## Freemium Notes

- Free users: core features (heatmap + immersion) are unlimited
- AI conversation: gated behind premium (`is_premium` in profiles table)
- To enable premium for testing: update the user's profile row in Supabase

---

## Next Steps (v2)

- [ ] SRS review session screen (flip cards)
- [ ] Stroke canvas for kanji practice (no ML scoring)
- [ ] Pronunciation coaching (Whisper)
- [ ] Push notifications for daily review reminders
- [ ] AI grammar error detection during conversation → auto-log to grammar_errors table
- [ ] Vocab extraction from immersion (NLP tagging pipeline)
