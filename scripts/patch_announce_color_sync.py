#!/usr/bin/env python3
"""Preserve color meta on save + hard cross-tab portal reload via tick key."""
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
changed = False

m = re.search(r"function stripChannelMeta\(body\?: string\): string \{[\s\S]*?\n\}", t)
if m:
    body = m.group(0)
    if "never strip color" not in body and "stripAllMeta" not in t[m.start():m.start()+500]:
        new = """function stripChannelMeta(body?: string): string {
  // Channel only — never strip color meta
  return (body || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .trim();
}

function stripAllMeta(body?: string): string {
  return (body || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .replace(/<!--\\s*nexus:color=[^>]+\\s*-->/gi, '')
    .trim();
}"""
        t = t[: m.start()] + new + t[m.end() :]
        changed = True
        print("strip helpers fixed")
    else:
        print("strip helpers already ok")

if "function stripAllMeta" not in t:
    m = re.search(r"function stripChannelMeta\(body\?: string\): string \{[\s\S]*?\n\}", t)
    if m:
        extra = """

function stripAllMeta(body?: string): string {
  return (body || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .replace(/<!--\\s*nexus:color=[^>]+\\s*-->/gi, '')
    .trim();
}"""
        t = t[: m.end()] + extra + t[m.end() :]
        changed = True
        print("stripAllMeta injected")

for a, b in [
    (
        "!fromDb.some((d) => stripChannelMeta(d.body) === stripChannelMeta(x.body))",
        "!fromDb.some((d) => stripAllMeta(d.body) === stripAllMeta(x.body))",
    ),
    (
        "(x.body === storedBody || stripChannelMeta(x.body) === plainBody)",
        "(x.body === storedBody || stripAllMeta(x.body) === stripAllMeta(plainBody))",
    ),
]:
    if a in t:
        t = t.replace(a, b)
        changed = True
        print("comparison fixed")

if "nexus-announce-tick" not in t[t.find("notifyAnnounceSync") : t.find("notifyAnnounceSync") + 500]:
    t2 = t.replace(
        """const notifyAnnounceSync = () => {
    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));""",
        """const notifyAnnounceSync = () => {
    try {
      localStorage.setItem('nexus-announce-tick', String(Date.now()));
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));""",
        1,
    )
    if t2 != t:
        t = t2
        changed = True
        print("notify tick added")

old_i = """    save(LS.announce, nextList);

    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));
      const bc = new BroadcastChannel('nexus-announce');
      bc.postMessage({ type: 'updated' });
      bc.close();
    } catch { /* ignore */ }

    if (!supabase) return;"""
new_i = """    save(LS.announce, nextList);
    notifyAnnounceSync();

    if (!supabase) return;"""
if old_i in t:
    t = t.replace(old_i, new_i)
    changed = True
    print("inline notify fixed")

if "nexus-announce-tick" not in t or "lastTick" not in t:
    m2 = re.search(
        r"  useEffect\(\(\) => \{\n    const isCustomerPortal = \(\) => \{[\s\S]*?\}, \[\]\);",
        t,
    )
    if not m2:
        m2 = re.search(
            r"  useEffect\(\(\) => \{\n    const pull = \(\) => \{[\s\S]*?setInterval\(pull, \d+\)[\s\S]*?\}, \[\]\);",
            t,
        )
    if m2:
        new_sync = """  useEffect(() => {
    const isCustomerPortal = () => {
      try {
        const h = window.location.hash || '';
        const p = window.location.pathname || '';
        return (
          /#\\/?portal\\b/i.test(h) ||
          /\\/portal\\b/i.test(p) ||
          !!document.querySelector('.portal-shell')
        );
      } catch {
        return false;
      }
    };
    const pull = () => {
      try {
        const next = mergeAnnouncementChannels(load(LS.announce, [] as Announcement[]));
        if (Array.isArray(next)) setAnnouncements(next);
      } catch { /* ignore */ }
    };
    let reloadTimer: number | undefined;
    let lastTick = '';
    try { lastTick = localStorage.getItem('nexus-announce-tick') || ''; } catch { /* ignore */ }
    let lastSnap = '';
    try { lastSnap = localStorage.getItem(LS.announce) || ''; } catch { /* ignore */ }
    const schedulePortalReload = () => {
      if (!isCustomerPortal()) { pull(); return; }
      pull();
      window.clearTimeout(reloadTimer);
      reloadTimer = window.setTimeout(() => {
        try { window.location.reload(); } catch { /* ignore */ }
      }, 350);
    };
    const onStorage = (e: StorageEvent) => {
      if (e.key === LS.announce || e.key === LS.announceChannels || e.key === 'nexus-announce-tick') {
        schedulePortalReload();
      }
    };
    const onCustom = () => schedulePortalReload();
    window.addEventListener('storage', onStorage);
    window.addEventListener('nexus-announce-updated', onCustom as EventListener);
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => schedulePortalReload();
    } catch { /* ignore */ }
    const tick = window.setInterval(() => {
      try {
        const tnow = localStorage.getItem('nexus-announce-tick') || '';
        const snap = localStorage.getItem(LS.announce) || '';
        if (tnow && tnow !== lastTick) { lastTick = tnow; schedulePortalReload(); return; }
        if (snap && snap !== lastSnap) {
          lastSnap = snap;
          if (isCustomerPortal()) schedulePortalReload();
          else pull();
        } else { pull(); }
      } catch { pull(); }
    }, 700);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('nexus-announce-updated', onCustom as EventListener);
      window.clearInterval(tick);
      window.clearTimeout(reloadTimer);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);"""
        t = t[: m2.start()] + new_sync + t[m2.end() :]
        changed = True
        print("sync effect with tick/poll")

if changed:
    p.write_text(t)
    print("written", len(t))
else:
    print("no change")
