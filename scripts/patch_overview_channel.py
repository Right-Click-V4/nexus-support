#!/usr/bin/env python3
from pathlib import Path
import re

p = Path("src/components/PortalHome.tsx")
t = p.read_text()
if "function resolveChannel" in t and "ch === 'portal' || ch === 'both'" in t:
    print("overview channel filter already present")
    raise SystemExit(0)

if "function resolveChannel" not in t:
    t = t.replace(
        "import { usePlatform } from '../context/PlatformContext';",
        """import { usePlatform } from '../context/PlatformContext';

function resolveChannel(a: { channel?: string; body?: string }) {
  const meta = (a.body || '').match(/^<!--nexus:channel=(\\w+)-->/);
  if (meta) return meta[1];
  return a.channel || 'both';
}

function displayBody(body?: string) {
  return (body || '').replace(/^<!--nexus:channel=\\w+-->\\n?/, '');
}
""",
        1,
    )

# Replace activeAnnouncements filter
pat = r"const activeAnnouncements = useMemo\([\s\S]*?\[announcements\],\s*\);"
repl = """const activeAnnouncements = useMemo(
    () =>
      (announcements || [])
        .filter((a) => {
          if (a.active === false) return false;
          const ch = resolveChannel(a);
          // Marquee-only must never show on the Overview card
          return ch === 'portal' || ch === 'both';
        })
        .slice(0, 4),
    [announcements],
  );"""
t2, n = re.subn(pat, repl, t, count=1)
if n:
    t = t2
    print("filter replaced")
else:
    print("filter pattern miss")

if "{displayBody(a.body)}" not in t:
    t = t.replace("{a.body}", "{displayBody(a.body)}", 1)
    print("displayBody wired")

p.write_text(t)
print("PortalHome channel filter done")
