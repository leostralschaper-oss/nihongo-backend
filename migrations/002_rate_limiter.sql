-- ============================================================
-- Persistent rate limiter — survives restarts & multi-instance
-- ============================================================

-- Track each AI request per user
create table if not exists public.ai_rate_events (
  id          bigserial primary key,
  user_id     uuid not null references auth.users(id) on delete cascade,
  event_at    timestamptz not null default now()
);

create index if not exists idx_rate_user_time
  on public.ai_rate_events (user_id, event_at desc);

-- Atomic check-and-increment in a single Postgres roundtrip.
-- Returns true if allowed, false if over quota.
create or replace function public.check_ai_rate_limit(
  uid uuid,
  max_per_hour int default 30
) returns boolean
language plpgsql
security definer
as $$
declare
  current_count int;
begin
  -- Count requests in the last hour
  select count(*) into current_count
    from public.ai_rate_events
   where user_id = uid
     and event_at > now() - interval '1 hour';

  if current_count >= max_per_hour then
    return false;
  end if;

  -- Log this request
  insert into public.ai_rate_events (user_id) values (uid);
  return true;
end;
$$;

-- Daily cleanup: drop events older than 24 hours
create or replace function public.cleanup_rate_events()
returns void language sql security definer as $$
  delete from public.ai_rate_events where event_at < now() - interval '24 hours';
$$;

-- RLS: users can never read this table directly (service role only)
alter table public.ai_rate_events enable row level security;
