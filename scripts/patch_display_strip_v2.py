#!/usr/bin/env python3
"""Aggressive strip of nexus meta from PortalHome + AnnouncementsPage displays."""
from pathlib import Path
import re

ph = Path("src/components/PortalHome.tsx")
if ph.exists():
    t = ph.read_text()
    m = re.search(r"function displayBody\(body\?: string\) \{[\s\S]*?\n\}", t)
    if m:
        t = t[: m.start()] + """function displayBody(body?: string) {
  return (body || '')
    .replace(/&lt;!--\\s*nexus:[^&]*--&gt;/gi, '')
    .replace(/<!--\\s*nexus:[^>]*-->/gi, '')
    .replace(/\\\\n/g, ' ')
    .trim();
}""" + t[m.end() :]
        print("ph displayBody")
    if "function bodyColor" in t:
        m = re.search(r"function bodyColor\([\s\S]*?\n\}", t)
        if m:
            t = t[: m.start()] + """function bodyColor(body?: string, title?: string): string | undefined {
  const src = body || title || '';
  const m = src.match(/<!--\\s*nexus:color=([#\\w(),.\\s%-]+)\\s*-->/i)
    || src.match(/&lt;!--\\s*nexus:color=([#\\w(),.\\s%-]+)\\s*--&gt;/i);
  return m?.[1]?.trim() || undefined;
}""" + t[m.end() :]
            print("ph bodyColor")
    t = t.replace("{a.title || 'Announcement'}", "{displayBody(a.title) || 'Announcement'}")
    t = t.replace("bodyColor(a.body)", "bodyColor(a.body, a.title)")
    ph.write_text(t)
    print("PortalHome done")

ann = Path("src/components/AnnouncementsPage.tsx")
if ann.exists():
    t = ann.read_text()
    m = re.search(r"function stripAnnounceMeta\(s\?: string\) \{[\s\S]*?\n\}", t)
    if m:
        t = t[: m.start()] + """function stripAnnounceMeta(s?: string) {
  return (s || '')
    .replace(/&lt;!--\\s*nexus:[^&]*--&gt;/gi, '')
    .replace(/<!--\\s*nexus:[^>]*-->/gi, '')
    .replace(/\\\\n/g, ' ')
    .trim();
}""" + t[m.end() :]
        print("ann strip")
    m = re.search(r"function announceColor\(s\?: string\): string \| undefined \{[\s\S]*?\n\}", t)
    if m:
        t = t[: m.start()] + """function announceColor(s?: string): string | undefined {
  const m = (s || '').match(/<!--\\s*nexus:color=([#\\w(),.\\s%-]+)\\s*-->/i)
    || (s || '').match(/&lt;!--\\s*nexus:color=([#\\w(),.\\s%-]+)\\s*--&gt;/i);
  return m?.[1]?.trim() || undefined;
}""" + t[m.end() :]
        print("ann color")
    ann.write_text(t)
    print("AnnouncementsPage done")
