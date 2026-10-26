#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()
if "h-screen max-h-screen overflow-hidden relative" in t and "h-full max-h-full overflow-hidden relative z-10" in t:
    print("already locked")
    raise SystemExit(0)
pairs = [
(
'className="app-cosmos flex min-h-screen relative"',
'className="app-cosmos flex h-screen max-h-screen overflow-hidden relative"',
),
(
'className="portal-shell flex-1 flex flex-col min-w-0 min-h-screen relative z-10"',
'className="portal-shell flex-1 flex flex-col min-w-0 h-full max-h-full overflow-hidden relative z-10"',
),
(
'className="portal-sidebar hidden md:flex w-60 shrink-0 flex-col relative z-30"',
'className="portal-sidebar hidden md:flex w-60 shrink-0 flex-col h-full max-h-screen overflow-hidden relative z-30"',
),
]
n = 0
for a, b in pairs:
    if a in t:
        t = t.replace(a, b, 1)
        n += 1
        print("patched", a[:50])
    else:
        print("miss", a[:50])
p.write_text(t)
print("done", n)
