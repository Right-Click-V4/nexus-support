-- Nexus Support — chat + missing columns (safe to re-run)
-- Fixes: chat_messages.body, chat_conversations.assignee_id, releases.body,
--        canned_responses.category, automations.active

-- Ensure chat tables exist (from schema-v2)
create table if not exists chat_conversations (
  id uuid primary key default gen_random_uuid(),
  customer_name text not null,
  customer_email text,
  status text not null default 'waiting',
  preview text default '',
  unread int default 0,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid references chat_conversations(id) on delete cascade,
  sender text not null,
  text text not null default '',
  created_at timestamptz default now()
);

-- Message body alias used by some code paths
alter table chat_messages add column if not exists body text;
update chat_messages set body = text where body is null and text is not null;
update chat_messages set text = body where (text is null or text = '') and body is not null;

-- Conversation fields the app expects
alter table chat_conversations add column if not exists assignee_id uuid;
alter table chat_conversations add column if not exists branch text;
alter table chat_conversations add column if not exists ticket_id text;
alter table chat_conversations add column if not exists archived_at timestamptz;
alter table chat_conversations add column if not exists preview text default '';
alter table chat_conversations add column if not exists unread int default 0;

do $$ begin
  alter table chat_conversations drop constraint if exists chat_conversations_status_check;
exception when undefined_object then null;
end $$;

alter table chat_conversations add constraint chat_conversations_status_check
  check (status in ('active','waiting','ended','archived','on_hold','open','closed'));

-- Other tables the app selects (avoid 42703 / 400 noise)
create table if not exists releases (
  id uuid primary key default gen_random_uuid(),
  title text,
  version text,
  body text default '',
  published_at timestamptz default now(),
  created_at timestamptz default now()
);
alter table releases add column if not exists body text;

create table if not exists canned_responses (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  body text not null default '',
  shortcut text,
  category text default 'general',
  created_at timestamptz default now()
);
alter table canned_responses add column if not exists category text default 'general';

create table if not exists automations (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  enabled boolean default true,
  active boolean default true,
  trigger text,
  condition_field text,
  condition_op text,
  condition_value text,
  action text,
  action_value text,
  created_at timestamptz default now()
);
alter table automations add column if not exists active boolean default true;
alter table automations add column if not exists enabled boolean default true;

-- Agents / customers approval columns (from earlier notes)
alter table agents add column if not exists approved_at timestamptz;
alter table agents add column if not exists user_id uuid;
alter table customers add column if not exists status text;
alter table customers add column if not exists approved_at timestamptz;
alter table customers add column if not exists user_id uuid;

-- RLS permissive (match existing app style)
alter table chat_conversations enable row level security;
alter table chat_messages enable row level security;
drop policy if exists cc_all on chat_conversations;
drop policy if exists cm_all on chat_messages;
create policy cc_all on chat_conversations for all using (true) with check (true);
create policy cm_all on chat_messages for all using (true) with check (true);

-- Optional realtime
do $$ begin
  alter publication supabase_realtime add table chat_conversations;
exception when duplicate_object then null; when undefined_object then null;
end $$;
do $$ begin
  alter publication supabase_realtime add table chat_messages;
exception when duplicate_object then null; when undefined_object then null;
end $$;
