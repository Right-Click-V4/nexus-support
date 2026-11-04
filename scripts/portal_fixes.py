#!/usr/bin/env python3
"""Portal fixes: My Tickets by email; wider agent online window."""
from pathlib import Path

cp = Path('src/components/CustomerPortal.tsx')
if cp.exists():
    t = cp.read_text()
    old = "const myTickets = isCustomerSession && user?.email ? ticketsForEmail(user.email) : [];"
    new = "const myTickets = user?.email ? ticketsForEmail(user.email) : [];"
    if old in t:
        cp.write_text(t.replace(old, new, 1))
        print('CustomerPortal: myTickets by email (not role-gated)')
    elif new in t:
        print('CustomerPortal: myTickets already fixed')
    else:
        print('CustomerPortal: myTickets pattern not found')
else:
    print('skip CustomerPortal')

pl = Path('src/components/PortalLiveChat.tsx')
if pl.exists():
    t = pl.read_text()
    n = 0
    for a, b in [
        ('const LIVE_WINDOW_MS = 180_000;', 'const LIVE_WINDOW_MS = 300_000;'),
        ('const LIVE_WINDOW_MS = 90_000;', 'const LIVE_WINDOW_MS = 300_000;'),
        ('const LIVE_WINDOW_MS = 120_000;', 'const LIVE_WINDOW_MS = 300_000;'),
    ]:
        if a in t:
            t = t.replace(a, b)
            n += 1
    if n:
        pl.write_text(t)
        print('PortalLiveChat: LIVE_WINDOW_MS -> 300s')
    else:
        print('PortalLiveChat: LIVE_WINDOW already ok or missing')
else:
    print('skip PortalLiveChat')

print('portal_fixes done')
