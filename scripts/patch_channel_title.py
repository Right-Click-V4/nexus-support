#!/usr/bin/env python3
from pathlib import Path
p = Path("src/context/PlatformContext.tsx")
t = p.read_text()
changed = False
if "map[`title:${a.title}`]" not in t:
    t2 = t.replace(
        "channel: a.channel || map[a.id] || 'both',",
        "channel: a.channel || map[a.id] || map[`title:${a.title}`] || 'both',",
        1,
    )
    if t2 != t:
        t = t2
        changed = True
    for old, new in [
        ("saveAnnounceChannel(tempId, channel);", "saveAnnounceChannel(tempId, channel);\n      saveAnnounceChannel(`title:${a.title}`, channel);"),
        ("saveAnnounceChannel(a.id, channel);", "saveAnnounceChannel(a.id, channel);\n      saveAnnounceChannel(`title:${a.title}`, channel);"),
        ("saveAnnounceChannel(data.id, channel);", "saveAnnounceChannel(data.id, channel);\n          saveAnnounceChannel(`title:${a.title}`, channel);"),
    ]:
        if old in t and new not in t:
            t = t.replace(old, new, 1)
            changed = True
if changed:
    p.write_text(t)
    print("platform channel title keys patched")
else:
    print("platform channel title keys already present")
