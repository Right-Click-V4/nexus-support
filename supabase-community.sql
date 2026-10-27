-- Nexus Ops: Community groups, members, messages (realtime-ready)
-- Run in Supabase SQL editor. Safe to re-run.

create table if not exists public.community_groups (
  id text primary key,
  name text not null,
  description text,
  created_by text not null default 'system',
  created_at timestamptz not null default now()
);

create table if not exists public.community_members (
  group_id text not null references public.community_groups(id) on delete cascade,
  email text not null,
  name text not null default '',
  joined_at timestamptz not null default now(),
  primary key (group_id, email)
);

create table if not exists public.community_messages (
  id text primary key,
  group_id text not null references public.community_groups(id) on delete cascade,
  author_name text not null default '',
  author_email text not null default '',
  body text not null default '',
  gif_url text,
  image_data text,
  pinned boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists community_messages_group_created_idx
  on public.community_messages (group_id, created_at);

create index if not exists community_members_email_idx
  on public.community_members (email);

insert into public.community_groups (id, name, description, created_by, created_at)
values (
  'default-nexus-community',
  'Nexus Community',
  'Default room for all customers — share tips and issues without opening a ticket.',
  'system',
  '1970-01-01T00:00:00Z'
)
on conflict (id) do nothing;

alter table public.community_groups enable row level security;
alter table public.community_members enable row level security;
alter table public.community_messages enable row level security;

drop policy if exists community_groups_select on public.community_groups;
drop policy if exists community_groups_write on public.community_groups;
drop policy if exists community_members_select on public.community_members;
drop policy if exists community_members_write on public.community_members;
drop policy if exists community_messages_select on public.community_messages;
drop policy if exists community_messages_write on public.community_messages;

create policy community_groups_select on public.community_groups
  for select to authenticated using (true);
create policy community_groups_write on public.community_groups
  for all to authenticated using (true) with check (true);

create policy community_members_select on public.community_members
  for select to authenticated using (true);
create policy community_members_write on public.community_members
  for all to authenticated using (true) with check (true);

create policy community_messages_select on public.community_messages
  for select to authenticated using (true);
create policy community_messages_write on public.community_messages
  for all to authenticated using (true) with check (true);

do $$
begin
  begin
    alter publication supabase_realtime add table public.community_groups;
  exception when duplicate_object then null;
  end;
  begin
    alter publication supabase_realtime add table public.community_members;
  exception when duplicate_object then null;
  end;
  begin
    alter publication supabase_realtime add table public.community_messages;
  exception when duplicate_object then null;
  end;
end $$;
