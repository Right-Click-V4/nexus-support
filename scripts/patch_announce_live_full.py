#!/usr/bin/env python3
"""Apply optional-title + live-sync patches to PlatformContext.tsx"""
from pathlib import Path

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
if "dbTitle" in t and "setInterval(pull" in t:
    print("already patched")
    raise SystemExit(0)

t = t.replace(
    "saveAnnouncement: (a: Partial<Announcement> & { title: string; body: string }) => Promise<void>;",
    "saveAnnouncement: (a: Partial<Announcement> & { body: string; title?: string }) => Promise<void>;",
)

start = t.find("  const saveAnnouncement = async")
if start < 0:
    raise SystemExit("saveAnnouncement not found")
end = t.find("  const deleteAnnouncement", start)
if end < 0:
    raise SystemExit("deleteAnnouncement not found")

new_fn = """  const saveAnnouncement = async (a: Partial<Announcement> & { body: string; title?: string }) => {
    const channel = a.channel || 'both';
    const severity = a.severity || 'info';
    const active = a.active ?? true;
    const title = (a.title || '').trim();
    const body = (a.body || '').trim();
    const dbTitle = title || body.slice(0, 80) || 'Announcement';

    if (!a.id) {
      const tempId = `an-${Date.now()}`;
      const optimistic: Announcement = {
        id: tempId,
        title,
        body,
        severity,
        active,
        channel,
        created_at: new Date().toISOString(),
      };
      setAnnouncements((prev) => [optimistic, ...prev]);
      saveAnnounceChannel(tempId, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${body.slice(0, 40)}`, channel);
    } else {
      setAnnouncements((prev) =>
        prev.map((x) => (x.id === a.id ? ({ ...x, ...a, title, body, channel, severity, active } as Announcement) : x)),
      );
      saveAnnounceChannel(a.id, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${body.slice(0, 40)}`, channel);
    }

    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
    } catch { /* ignore */ }

    if (!supabase) return;

    const row = { title: dbTitle, body, severity, active };
    try {
      if (a.id) {
        const { error } = await supabase.from('announcements').update(row).eq('id', a.id);
        if (error) throw error;
      } else {
        const { data, error } = await supabase.from('announcements').insert(row).select('*').single();
        if (error) throw error;
        if (data?.id) {
          saveAnnounceChannel(data.id, channel);
          if (title) saveAnnounceChannel(`title:${title}`, channel);
          saveAnnounceChannel(`body:${body.slice(0, 40)}`, channel);
          setAnnouncements((prev) =>
            prev.map((x) =>
              x.body === body && String(x.id).startsWith('an-')
                ? ({ ...x, ...data, title, body, channel } as Announcement)
                : x,
            ),
          );
        }
      }
      await refreshPlatform();
    } catch (err) {
      console.error('saveAnnouncement failed', err);
    }
  };
"""

t = t[:start] + new_fn + "\n" + t[end:]

t = t.replace(
    "channel: a.channel || map[a.id] || 'both',",
    "channel: a.channel || map[a.id] || (a.title && map[`title:${a.title}`]) || map[`body:${(a.body || '').slice(0, 40)}`] || 'both',",
)
t = t.replace(
    "channel: a.channel || map[a.id] || map[`title:${a.title}`] || 'both',",
    "channel: a.channel || map[a.id] || (a.title && map[`title:${a.title}`]) || map[`body:${(a.body || '').slice(0, 40)}`] || 'both',",
)

if "setInterval(pull" not in t:
    marker = "  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
    sync = """
  useEffect(() => {
    const pull = () => {
      try {
        const next = mergeAnnouncementChannels(load(LS.announce, [] as Announcement[]));
        if (Array.isArray(next)) setAnnouncements(next);
      } catch { /* ignore */ }
    };
    const onStorage = (e: StorageEvent) => {
      if (e.key === LS.announce || e.key === LS.announceChannels) pull();
    };
    const onCustom = () => pull();
    window.addEventListener('storage', onStorage);
    window.addEventListener('nexus-announce-updated', onCustom as EventListener);
    const tick = window.setInterval(pull, 2000);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('nexus-announce-updated', onCustom as EventListener);
      window.clearInterval(tick);
    };
  }, []);
"""
    if marker in t:
        t = t.replace(marker, marker + "\n" + sync, 1)

p.write_text(t)
print("patched PlatformContext", len(t))
