#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
if "parseChannelFromBody" in t and "setInterval(pull, 1000)" in t and "bc.onmessage" in t:
    print("v3 already")
    raise SystemExit(0)

m = re.search(r"function mergeAnnouncementChannels\(list: Announcement\[\]\): Announcement\[] \{[\s\S]*?\n\}", t)
if not m:
    raise SystemExit("no merge")
helpers = """function stripChannelMeta(body?: string): string {
  return (body || '').replace(/^<!--nexus:channel=\\w+-->\\n?/, '');
}

function parseChannelFromBody(body?: string): 'marquee' | 'portal' | 'both' | null {
  const m = (body || '').match(/^<!--nexus:channel=(\\w+)-->/);
  if (!m) return null;
  if (m[1] === 'marquee' || m[1] === 'portal' || m[1] === 'both') return m[1];
  return null;
}

function mergeAnnouncementChannels(list: Announcement[]): Announcement[] {
  const map = loadAnnounceChannels();
  return list.map((a) => {
    const fromBody = parseChannelFromBody(a.body);
    const channel =
      a.channel ||
      fromBody ||
      map[a.id] ||
      (a.title && map[`title:${a.title}`]) ||
      map[`body:${stripChannelMeta(a.body).slice(0, 40)}`] ||
      'both';
    return { ...a, channel, body: a.body };
  });
}"""
t = t[:m.start()] + helpers + t[m.end():]

start = t.find("  const saveAnnouncement = async")
end = t.find("  const deleteAnnouncement", start)
if start < 0 or end < 0:
    raise SystemExit("no saveAnnouncement")

new_fn = """  const saveAnnouncement = async (a: Partial<Announcement> & { body: string; title?: string }) => {
    const channel = a.channel || 'both';
    const severity = a.severity || 'info';
    const active = a.active ?? true;
    const title = (a.title || '').trim();
    const plainBody = stripChannelMeta(a.body || '').trim();
    const storedBody =
      channel === 'both' ? plainBody : `<!--nexus:channel=${channel}-->\\n${plainBody}`;
    const dbTitle = title || plainBody.slice(0, 80) || 'Announcement';

    let nextList: Announcement[] = [];
    if (!a.id) {
      const tempId = `an-${Date.now()}`;
      const optimistic: Announcement = {
        id: tempId, title, body: storedBody, severity, active, channel,
        created_at: new Date().toISOString(),
      };
      nextList = [optimistic, ...announcements];
      setAnnouncements(nextList);
      saveAnnounceChannel(tempId, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
    } else {
      nextList = announcements.map((x) =>
        x.id === a.id ? ({ ...x, ...a, title, body: storedBody, channel, severity, active } as Announcement) : x,
      );
      setAnnouncements(nextList);
      saveAnnounceChannel(a.id, channel);
      if (title) saveAnnounceChannel(`title:${title}`, channel);
      saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
    }

    save(LS.announce, nextList);

    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
      const bc = new BroadcastChannel('nexus-announce');
      bc.postMessage({ type: 'updated' });
      bc.close();
    } catch { /* ignore */ }

    if (!supabase) return;

    const row = { title: dbTitle, body: storedBody, severity, active };
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
          saveAnnounceChannel(`body:${plainBody.slice(0, 40)}`, channel);
          setAnnouncements((prev) => {
            const merged = prev.map((x) =>
              (x.body === storedBody || stripChannelMeta(x.body) === plainBody) && String(x.id).startsWith('an-')
                ? ({ ...x, ...data, title, body: storedBody, channel } as Announcement)
                : x,
            );
            save(LS.announce, merged);
            return merged;
          });
        }
      }
      await refreshPlatform();
    } catch (err) {
      console.error('saveAnnouncement failed', err);
    }
  };
"""
t = t[:start] + new_fn + "\n" + t[end:]

sync = """  useEffect(() => {
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
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => pull();
    } catch { /* ignore */ }
    const tick = window.setInterval(pull, 1000);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('nexus-announce-updated', onCustom as EventListener);
      window.clearInterval(tick);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);
"""
m2 = re.search(r"  useEffect\(\(\) => \{\n    const pull = \(\) => \{[\s\S]*?setInterval\(pull, \d+\);[\s\S]*?\}, \[\]\);", t)
if m2:
    t = t[:m2.start()] + sync + t[m2.end():]
    print("sync replaced")
elif "setInterval(pull, 1000)" not in t:
    marker = "  useEffect(() => { if (isSupabaseConfigured) void refreshPlatform(); }, [refreshPlatform]);"
    if marker in t:
        t = t.replace(marker, marker + "\n\n" + sync, 1)
        print("sync inserted")

t = t.replace(
    "saveAnnouncement: (a: Partial<Announcement> & { title: string; body: string }) => Promise<void>;",
    "saveAnnouncement: (a: Partial<Announcement> & { body: string; title?: string }) => Promise<void>;",
)

p.write_text(t)
print("done", len(t))
