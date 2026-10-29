#!/usr/bin/env python3
"""Tickets sidebar badge = new/unread tickets only; decreases when agent opens."""
from pathlib import Path

p = Path("src/SystemApp.tsx")
c = p.read_text()
if "tickets-badge-unread-v1" in c:
    print("already")
    raise SystemExit(0)

old = "  const openCount = tickets.filter((t) => t.status !== 'resolved' && !t.deleted_at).length;"
new = """  /* Badge: New or unopened (unread tag) tickets only — clears when agent opens the ticket */
  const openCount = tickets.filter(
    (t) =>
      !t.deleted_at &&
      (t.status === 'new' || (t.tags || []).includes('unread'))
  ).length;"""

if old in c:
    c = c.replace(old, new, 1)
    print("openCount ok")
else:
    print("openCount miss")

c = "/* tickets-badge-unread-v1 */\n" + c
p.write_text(c)
print("done")
