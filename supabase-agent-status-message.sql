-- Run once in Supabase SQL Editor (Dashboard → SQL → New query → Run)
-- Agent presence: session Online/Offline + Away / Busy / In a Call / Custom

-- Allow new presence values on agents.status
alter table public.agents drop constraint if exists agents_status_check;

alter table public.agents
  add constraint agents_status_check
  check (status in ('online', 'busy', 'away', 'in_call', 'custom', 'offline'));

-- Optional note when status is "custom" (or short note next to presence)
alter table public.agents
  add column if not exists status_message text;

comment on column public.agents.status_message is
  'Optional custom presence text shown in Live Chat Active now card';

comment on column public.agents.status is
  'online = available in workspace; offline = logged out / no session; away|busy|in_call|custom = while logged in';
