-- Run once in Supabase SQL Editor
-- Accurate Live Chat "Active now" presence

alter table public.agents
  add column if not exists last_seen_at timestamptz;

comment on column public.agents.last_seen_at is
  'Updated every ~15s while agent has Agent Workspace open; Active Now requires recent last_seen';

-- Optional: mark everyone offline once so stale Online/Busy rows clear until they log in again
update public.agents
set status = 'offline',
    last_seen_at = null
where coalesce(status, '') <> 'offline';
