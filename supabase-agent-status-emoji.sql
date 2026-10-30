-- Run once in Supabase SQL Editor
alter table public.agents
  add column if not exists status_emoji text;

comment on column public.agents.status_emoji is
  'Optional emoji shown beside status in Live Chat Active Now';
