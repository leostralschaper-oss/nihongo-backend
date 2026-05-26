-- ============================================================
-- Nihongo App — Supabase Database Schema
-- Run this in the Supabase SQL Editor
-- ============================================================

-- Enable UUID extension
create extension if not exists "pgcrypto";

-- ============================================================
-- USERS PROFILE (extends Supabase auth.users)
-- ============================================================
create table if not exists public.profiles (
  id              uuid primary key references auth.users(id) on delete cascade,
  display_name    text,
  avatar_url      text,
  difficulty      text not null default 'beginner'
                    check (difficulty in ('beginner', 'intermediate', 'advanced')),
  ai_personality  text not null default 'friendly_teacher'
                    check (ai_personality in ('friendly_teacher', 'anime_character', 'business_mentor')),
  total_xp        integer not null default 0,
  level           integer not null default 1,
  is_premium      boolean not null default false,
  created_at      timestamptz not null default now(),
  last_active_at  timestamptz
);

-- Auto-create profile on signup
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.profiles (id, display_name)
  values (new.id, new.raw_user_meta_data->>'display_name');
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- ============================================================
-- VOCAB CARDS (SRS deck)
-- ============================================================
create table if not exists public.vocab_cards (
  id                    uuid primary key default gen_random_uuid(),
  user_id               uuid not null references auth.users(id) on delete cascade,
  word                  text not null,
  reading               text not null,
  meaning               text not null,
  example_sentence      text,
  example_reading       text,
  example_translation   text,
  jlpt_level            text check (jlpt_level in ('N5','N4','N3','N2','N1')),
  tags                  text[] not null default '{}',

  -- SM-2 SRS fields
  repetitions           integer not null default 0,
  interval_days         integer not null default 1,
  ease_factor           numeric(4,3) not null default 2.5,
  memory_strength       numeric(4,3) not null default 1.0, -- 0.0 – 1.0
  next_review_at        timestamptz not null default now() + interval '1 day',
  last_reviewed_at      timestamptz,
  learned_at            timestamptz not null default now(),

  unique (user_id, word)
);

create index on public.vocab_cards (user_id, next_review_at);
create index on public.vocab_cards (user_id, memory_strength);

-- ============================================================
-- REVIEW LOGS
-- ============================================================
create table if not exists public.review_logs (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references auth.users(id) on delete cascade,
  card_id       uuid not null references public.vocab_cards(id) on delete cascade,
  quality       integer not null check (quality between 0 and 5),
  interval_days integer not null,
  ease_factor   numeric(4,3) not null,
  reviewed_at   timestamptz not null default now()
);

create index on public.review_logs (user_id, reviewed_at);

-- ============================================================
-- GRAMMAR ERRORS (tracks repeated mistakes from AI chat)
-- ============================================================
create table if not exists public.grammar_errors (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  pattern     text not null,  -- e.g. 'te_form', 'passive', 'particle_wa_ga'
  count       integer not null default 1,
  last_seen   timestamptz not null default now(),

  unique (user_id, pattern)
);

-- Upsert function for grammar error tracking
create or replace function public.increment_grammar_error(p_user_id uuid, p_pattern text)
returns void language plpgsql as $$
begin
  insert into public.grammar_errors (user_id, pattern, count)
  values (p_user_id, p_pattern, 1)
  on conflict (user_id, pattern)
  do update set count = grammar_errors.count + 1, last_seen = now();
end;
$$;

-- ============================================================
-- IMMERSION CONTENT
-- ============================================================
create table if not exists public.immersion_content (
  id            uuid primary key default gen_random_uuid(),
  category      text not null check (category in ('anime','travel','daily_life','news','business')),
  title         text not null,           -- English title
  title_ja      text not null,           -- Japanese title
  image_url     text,
  audio_url     text,
  source_url    text,
  difficulty    text check (difficulty in ('N5','N4','N3','N2','N1')),
  vocab_ids     uuid[] not null default '{}',
  published_at  timestamptz not null default now(),
  created_at    timestamptz not null default now()
);

create index on public.immersion_content (category, published_at desc);

-- ============================================================
-- IMMERSION SEGMENTS (individual sentences within content)
-- ============================================================
create table if not exists public.immersion_segments (
  id                  uuid primary key default gen_random_uuid(),
  content_id          uuid not null references public.immersion_content(id) on delete cascade,
  index               integer not null,
  japanese            text not null,
  reading             text not null,
  translation         text not null,
  words               jsonb not null default '[]',  -- array of SegmentWord objects
  start_time_seconds  numeric,
  end_time_seconds    numeric
);

create index on public.immersion_segments (content_id, index);

-- ============================================================
-- ROW LEVEL SECURITY
-- ============================================================

-- Profiles: users can only see/edit their own
alter table public.profiles enable row level security;
drop policy if exists "profiles_own" on public.profiles;
create policy "profiles_own" on public.profiles
  for all using (auth.uid() = id);

-- Vocab cards: users can only see/edit their own
alter table public.vocab_cards enable row level security;
drop policy if exists "vocab_own" on public.vocab_cards;
create policy "vocab_own" on public.vocab_cards
  for all using (auth.uid() = user_id);

-- Review logs: users can only see their own
alter table public.review_logs enable row level security;
drop policy if exists "reviews_own" on public.review_logs;
create policy "reviews_own" on public.review_logs
  for all using (auth.uid() = user_id);

-- Grammar errors: users can only see their own
alter table public.grammar_errors enable row level security;
drop policy if exists "grammar_own" on public.grammar_errors;
create policy "grammar_own" on public.grammar_errors
  for all using (auth.uid() = user_id);

-- Immersion content: public read, admin write
alter table public.immersion_content enable row level security;
drop policy if exists "immersion_read" on public.immersion_content;
create policy "immersion_read" on public.immersion_content
  for select using (true);

alter table public.immersion_segments enable row level security;
drop policy if exists "segments_read" on public.immersion_segments;
create policy "segments_read" on public.immersion_segments
  for select using (true);

-- ============================================================
-- SAMPLE IMMERSION DATA (for testing)
-- ============================================================
insert into public.immersion_content (category, title, title_ja, difficulty)
values
  ('anime', 'A Day at School', '学校の一日', 'N4'),
  ('travel', 'Arriving at Tokyo Station', '東京駅に着く', 'N5'),
  ('daily_life', 'Cooking Ramen at Home', '家でラーメンを作る', 'N5'),
  ('news', 'Cherry Blossom Season Begins', '桜の季節が始まる', 'N3'),
  ('business', 'Starting a Meeting', '会議を始める', 'N3');
