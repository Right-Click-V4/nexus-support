-- Optional: add channel column for announcement targeting (marquee / portal / both)
alter table announcements
  add column if not exists channel text default 'both';

comment on column announcements.channel is 'marquee | portal | both';
