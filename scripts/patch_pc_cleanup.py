#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()

m = re.search(
    r"function saveAnnounceChannel[\s\S]*?save\(LS\.announceChannels, map\);\n\}",
    t,
)
kb = t.find("const DEFAULT_KB")
if not m or kb < 0:
    raise SystemExit(f"markers missing save={bool(m)} kb={kb}")

helpers = """

function stripChannelMeta(body?: string): string {
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
}

function parseChannelFromBody(body?: string): 'marquee' | 'portal' | 'both' | null {
  const m = (body || '').match(/<!--\\s*nexus:channel=(\\w+)\\s*-->/i);
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
      map[`body:${stripAllMeta(a.body).slice(0, 40)}`] ||
      'both';
    return { ...a, channel, body: a.body };
  });
}

"""

t = t[: m.end()] + helpers + t[kb:]

if "lastTick" not in t:
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
        print("reload wired")

if "nexus-announce-tick" not in t[t.find("const notifyAnnounceSync"):t.find("const notifyAnnounceSync")+400]:
    t = t.replace(
        """const notifyAnnounceSync = () => {
    try {
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));""",
        """const notifyAnnounceSync = () => {
    try {
      localStorage.setItem('nexus-announce-tick', String(Date.now()));
      window.dispatchEvent(new CustomEvent('nexus-announce-updated'));""",
        1,
    )
    print("notify tick added")

assert t.count("function stripChannelMeta") == 1
assert t.count("function stripAllMeta") == 1
assert t.count("function parseChannelFromBody") == 1
assert t.count("function mergeAnnouncementChannels") == 1

p.write_text(t)
print("cleaned", len(t), "tick", t.count("nexus-announce-tick"))
