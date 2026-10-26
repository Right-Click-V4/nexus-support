#!/usr/bin/env python3
from pathlib import Path
p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
if "dbTitle" in t and "nexus-announce-updated" in t and "setInterval(pull" in t:
    print("announce live already present")
    raise SystemExit(0)
sidecar = Path("scripts/_pc_announce_live.tsx")
if sidecar.exists():
    p.write_text(sidecar.read_text())
    print("platform context replaced from sidecar")
else:
    # inline minimal fixes if sidecar absent
    t = t.replace(
        "saveAnnouncement: (a: Partial<Announcement> & { title: string; body: string }) => Promise<void>;",
        "saveAnnouncement: (a: Partial<Announcement> & { body: string; title?: string }) => Promise<void>;",
        1,
    )
    p.write_text(t)
    print("partial signature patch only")
