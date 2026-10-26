#!/usr/bin/env python3
from pathlib import Path
p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
if "channel: a.channel || 'both'" in t:
    print("platform already has channel")
else:
    old = """  const saveAnnouncement = async (a: Partial<Announcement> & { title: string; body: string }) => {
    if (supabase) {
      if (a.id) await supabase.from('announcements').update(a).eq('id', a.id);
      else await supabase.from('announcements').insert({ title: a.title, body: a.body, severity: a.severity || 'info', active: a.active ?? true });
      await refreshPlatform();
    } else setAnnouncements((prev) => a.id ? prev.map((x) => (x.id === a.id ? { ...x, ...a } as Announcement : x)) : [{ id: `an-${Date.now()}`, severity: 'info', active: true, created_at: new Date().toISOString(), ...a } as Announcement, ...prev]);
  };"""
    new = """  const saveAnnouncement = async (a: Partial<Announcement> & { title: string; body: string }) => {
    if (supabase) {
      const row = {
        title: a.title,
        body: a.body,
        severity: a.severity || 'info',
        active: a.active ?? true,
        channel: a.channel || 'both',
      };
      if (a.id) await supabase.from('announcements').update({ ...row, ...a }).eq('id', a.id);
      else await supabase.from('announcements').insert(row);
      await refreshPlatform();
    } else setAnnouncements((prev) => a.id ? prev.map((x) => (x.id === a.id ? { ...x, ...a } as Announcement : x)) : [{ id: `an-${Date.now()}`, severity: 'info', active: true, channel: a.channel || 'both', created_at: new Date().toISOString(), ...a } as Announcement, ...prev]);
  };"""
    if old not in t:
        raise SystemExit("saveAnnouncement block not found")
    t = t.replace(old, new, 1)
    t = t.replace(
        "{ id: 'an1', title: 'Welcome', body: 'Share #/portal with customers.', severity: 'info', active: true, created_at: new Date().toISOString() }",
        "{ id: 'an1', title: 'Welcome', body: 'Share #/portal with customers.', severity: 'info', active: true, channel: 'both', created_at: new Date().toISOString() }",
        1,
    )
    p.write_text(t)
    print("platform channel patched")

ph = Path("src/components/PortalHome.tsx")
if ph.exists():
    h = ph.read_text()
    oldf = "() => (announcements || []).filter((a) => a.active !== false).slice(0, 4),"
    newf = "() => (announcements || []).filter((a) => a.active !== false && (a.channel === 'portal' || a.channel === 'both' || !a.channel)).slice(0, 4),"
    if oldf in h:
        ph.write_text(h.replace(oldf, newf, 1))
        print("portal home filtered")
    elif "channel === 'portal'" in h:
        print("portal home already filtered")
    else:
        print("portal home filter anchor missing")
