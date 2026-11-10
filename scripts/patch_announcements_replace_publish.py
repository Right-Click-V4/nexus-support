#!/usr/bin/env python3
from pathlib import Path
p = Path('src/components/AnnouncementsPage.tsx')
if not p.exists():
    raise SystemExit(0)
s = p.read_text()
old = """      await saveRelease({
        version: version.trim(),
        title: relTitle.trim(),
        notes: n,
      });"""
new = """      if (releases?.length) {
        for (const r of [...releases]) {
          try { await deleteRelease(r.id); } catch { /* ignore */ }
        }
      }
      await saveRelease({
        version: version.trim(),
        title: relTitle.trim(),
        notes: n,
      });"""
if old in s and 'if (releases?.length)' not in s:
    p.write_text(s.replace(old, new, 1))
    print('announcements: replace-on-publish enabled')
else:
    print('announcements: ok')
