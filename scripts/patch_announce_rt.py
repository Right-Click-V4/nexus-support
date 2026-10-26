#!/usr/bin/env python3
"""Realtime announce: optimistic delete, faster poll, soft DB merge."""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
changed = False

if "const next = announcements.filter((x) => x.id !== id)" not in t:
    m = re.search(r"  const deleteAnnouncement = async \(id: string\) => \{[\s\S]*?\n  \};", t)
    if not m:
        raise SystemExit("deleteAnnouncement not found")
    old = m.group(0)
    new = """  const notifyAnnounceSync = () => {
    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
      const bc = new BroadcastChannel('nexus-announce');
      bc.postMessage({ type: 'updated', t: Date.now() });
      bc.close();
    } catch { /* ignore */ }
  };

  const deleteAnnouncement = async (id: string) => {
    const next = announcements.filter((x) => x.id !== id);
    setAnnouncements(next);
    save(LS.announce, next);
    notifyAnnounceSync();
    if (!supabase) return;
    try {
      await supabase.from('announcements').delete().eq('id', id);
      void refreshPlatform();
    } catch (err) {
      console.error('deleteAnnouncement failed', err);
    }
  };"""
    t = t.replace(old, new, 1)
    changed = True
    print("delete patched")

if "notifyAnnounceSync()" not in t:
    t2 = t.replace(
        """    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
      const bc = new BroadcastChannel('nexus-announce');
      bc.postMessage({ type: 'updated' });
      bc.close();
    } catch { /* ignore */ }

    if (!supabase) return;""",
        """    notifyAnnounceSync();

    if (!supabase) return;""",
        1,
    )
    if t2 != t:
        t = t2
        changed = True
        print("save notify wired")

if "const notifyAnnounceSync" in t and t.find("const notifyAnnounceSync") > t.find("const saveAnnouncement"):
    start = t.find("  const notifyAnnounceSync = () => {")
    end = t.find("  const deleteAnnouncement", start)
    if start > 0 and end > start:
        block = t[start:end]
        t = t[:start] + t[end:]
        ins = t.find("  const saveAnnouncement = async")
        t = t[:ins] + block + "\n" + t[ins:]
        changed = True
        print("notify moved before save")

if "setInterval(pull, 500)" not in t:
    t2 = re.sub(r"setInterval\(pull, \d+\)", "setInterval(pull, 500)", t, count=1)
    if t2 != t:
        t = t2
        changed = True
        print("poll 500ms")

if "optimistic temp" not in t.lower() and "String(x.id).startsWith('an-')" not in t[t.find("if (ann.data)"):t.find("if (ann.data)")+800]:
    old = "    if (ann.data) setAnnouncements(mergeAnnouncementChannels(ann.data as Announcement[]));"
    new = """    if (ann.data) {
      const fromDb = mergeAnnouncementChannels(ann.data as Announcement[]);
      setAnnouncements((prev) => {
        const temps = prev.filter(
          (x) =>
            String(x.id).startsWith('an-') &&
            !fromDb.some((d) => stripChannelMeta(d.body) === stripChannelMeta(x.body)),
        );
        const merged = [...temps, ...fromDb];
        const seen = new Set<string>();
        const out: Announcement[] = [];
        for (const a of merged) {
          if (seen.has(a.id)) continue;
          seen.add(a.id);
          out.push(a);
        }
        return out;
      });
    }"""
    if old in t:
        t = t.replace(old, new, 1)
        changed = True
        print("soft merge")

if changed:
    p.write_text(t)
    print("written", len(t))
else:
    print("no changes needed")
