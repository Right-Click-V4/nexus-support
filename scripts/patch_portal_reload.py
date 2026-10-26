#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
changed = False

m = re.search(r"function stripChannelMeta\(body\?: string\): string \{[\s\S]*?\n\}", t)
if m and "nexus:color" not in m.group(0):
    new_strip = """function stripChannelMeta(body?: string): string {
  return (body || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .replace(/<!--\\s*nexus:color=[^>]+\\s*-->/gi, '')
    .trim();
}"""
    t = t[: m.start()] + new_strip + t[m.end() :]
    changed = True
    print("strip fixed")

if "schedulePortalReload" not in t:
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
    const schedulePortalReload = () => {
      if (!isCustomerPortal()) {
        pull();
        return;
      }
      pull();
      window.clearTimeout(reloadTimer);
      reloadTimer = window.setTimeout(() => {
        try {
          window.location.reload();
        } catch { /* ignore */ }
      }, 400);
    };

    const onStorage = (e: StorageEvent) => {
      if (e.key === LS.announce || e.key === LS.announceChannels) schedulePortalReload();
    };
    const onCustom = () => schedulePortalReload();
    window.addEventListener('storage', onStorage);
    window.addEventListener('nexus-announce-updated', onCustom as EventListener);
    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => schedulePortalReload();
    } catch { /* ignore */ }
    const tick = window.setInterval(pull, 800);
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
        print("portal reload wired")
    else:
        print("sync effect not found")
else:
    print("reload already present")

if changed:
    p.write_text(t)
    print("written", len(t))
else:
    print("no file change")
