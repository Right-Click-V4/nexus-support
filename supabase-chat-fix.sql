-- Run in Supabase SQL Editor to align chat schema with the app
alter table chat_conversations add column if not exists branch text;
alter table chat_conversations add column if not exists ticket_id text;
alter table chat_conversations add column if not exists archived_at timestamptz;

do $$ begin
  alter table chat_conversations drop constraint if exists chat_conversations_status_check;
exception when undefined_object then null;
end $$;

alter table chat_conversations add constraint chat_conversations_status_check
  check (status in ('active','waiting','ended','archived','on_hold','open','closed'));
