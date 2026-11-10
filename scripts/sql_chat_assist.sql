-- Optional: multi-agent assist columns on chat_conversations
-- Run in Supabase SQL editor if claim/assist should persist across browsers.

alter table public.chat_conversations
  add column if not exists agent_id text;

alter table public.chat_conversations
  add column if not exists assistant_ids jsonb default '[]'::jsonb;

alter table public.chat_conversations
  add column if not exists assist_requests jsonb default '[]'::jsonb;

alter table public.chat_conversations
  add column if not exists updated_at timestamptz default now();
