#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/PortalLiveChat.tsx")
if not p.exists():
    raise SystemExit(0)
t = p.read_text()
old = """disabled={isOnHold} onClick={() => void send()}
                disabled={!draft.trim()}"""
new = """disabled={isOnHold || !draft.trim()} onClick={() => void send()}"""
if old in t:
    t = t.replace(old, new, 1)
    p.write_text(t)
    print("fixed duplicate disabled")
else:
    print("portal disabled ok or different")
