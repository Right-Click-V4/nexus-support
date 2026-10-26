#!/usr/bin/env python3
from pathlib import Path
import re

ph = Path("src/components/PortalHome.tsx")
if ph.exists():
    t = ph.read_text()
    if "function bodyColor" not in t:
        m = re.search(r"function displayBody\(body\?: string\) \{[\s\S]*?\n\}", t)
        if m:
            t = t[: m.start()] + """function displayBody(body?: string) {
  return (body || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .replace(/<!--\\s*nexus:color=[^>]+\\s*-->/gi, '')
    .replace(/\\\\n/g, ' ')
    .trim();
}

function bodyColor(body?: string): string | undefined {
  const m = (body || '').match(/<!--\\s*nexus:color=([^>\\s]+)\\s*-->/i);
  return m?.[1]?.trim() || undefined;
}""" + t[m.end() :]
        if "{displayBody(a.body)}" in t and "bodyColor(a.body)" not in t:
            t = t.replace(
                "{displayBody(a.body)}",
                '<span style={bodyColor(a.body) ? { color: bodyColor(a.body) } : undefined}>{displayBody(a.body)}</span>',
                1,
            )
        ph.write_text(t)
        print("PortalHome patched")
    else:
        print("PortalHome already")

ann = Path("src/components/AnnouncementsPage.tsx")
if ann.exists():
    t = ann.read_text()
    if "function stripAnnounceMeta" not in t:
        t = t.replace(
            "type Channel = 'marquee' | 'portal' | 'both';",
            """function stripAnnounceMeta(s?: string) {
  return (s || '')
    .replace(/<!--\\s*nexus:channel=\\w+\\s*-->/gi, '')
    .replace(/<!--\\s*nexus:color=[^>]+\\s*-->/gi, '')
    .replace(/\\\\n/g, '\\n')
    .trim();
}

function announceColor(s?: string): string | undefined {
  const m = (s || '').match(/<!--\\s*nexus:color=([^>\\s]+)\\s*-->/i);
  return m?.[1]?.trim() || undefined;
}

type Channel = 'marquee' | 'portal' | 'both';
""",
            1,
        )
    t2, n = re.subn(
        r"<p\s+className=\"text-sm text-slate-600 mt-1 whitespace-pre-wrap\"[\s\S]*?</p>",
        """<p
              className=\"text-sm text-slate-600 mt-1 whitespace-pre-wrap\"
              style={announceColor(a.body) ? { color: announceColor(a.body) } : undefined}
            >
              {stripAnnounceMeta(a.body)}
            </p>""",
        t,
        count=1,
    )
    if n:
        t = t2
        print("ann body", n)
    t2, n = re.subn(
        r"<p\s+className=\"text-sm text-slate-600 mt-1\.5 whitespace-pre-wrap\"[\s\S]*?</p>",
        """<p
                  className=\"text-sm text-slate-600 mt-1.5 whitespace-pre-wrap\"
                  style={announceColor(r.notes) ? { color: announceColor(r.notes) } : undefined}
                >
                  {stripAnnounceMeta(r.notes)}
                </p>""",
        t,
        count=1,
    )
    if n:
        t = t2
        print("ann notes", n)
    ann.write_text(t)
    print("AnnouncementsPage done")
