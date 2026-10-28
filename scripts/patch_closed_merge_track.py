#!/usr/bin/env python3
"""SLA-breached tickets show Closed + red; remove Track Ticket from portal nav."""
from pathlib import Path

types = Path("src/types.ts")
if types.exists():
    t = types.read_text()
    if "'closed'" not in t.split("export type Status")[1][:120]:
        t = t.replace(
            "export type Status = 'new' | 'open' | 'pending' | 'resolved' | 'on-hold';",
            "export type Status = 'new' | 'open' | 'pending' | 'resolved' | 'on-hold' | 'closed';",
            1,
        )
        types.write_text(t)
        print("types ok")
    else:
        print("types already")

tp = Path("src/components/TicketsPage.tsx")
p = tp.read_text()
if "closed-sla-v1" not in p:
    if "'on-hold': 'bg-slate-50 text-slate-600 border-slate-200'," in p and "closed:" not in p.split("statusStyles")[1][:400]:
        p = p.replace(
            "'on-hold': 'bg-slate-50 text-slate-600 border-slate-200',\n};",
            "'on-hold': 'bg-slate-50 text-slate-600 border-slate-200',\n  closed: 'bg-rose-50 text-rose-700 border-rose-200',\n};",
            1,
        )
        print("statusStyles ok")

    old_row = """                    className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      (t.status === 'open' || t.status === 'new') && 'tickets-row-open',
                      t.status === 'pending' && 'tickets-row-pending',
                      t.status === 'on-hold' && 'tickets-row-onhold',
                      t.status === 'resolved' && 'tickets-row-resolved',
                      ((t.tags || []).includes('unread') || t.status === 'new') && 'tickets-row-unread'
                    )}"""
    new_row = """                    className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      (sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                        ? 'tickets-row-closed'
                        : clsx(
                            (t.status === 'open' || t.status === 'new') && 'tickets-row-open',
                            t.status === 'pending' && 'tickets-row-pending',
                            t.status === 'on-hold' && 'tickets-row-onhold',
                            t.status === 'resolved' && 'tickets-row-resolved',
                          ),
                      ((t.tags || []).includes('unread') || t.status === 'new') && 'tickets-row-unread'
                    )}"""
    if old_row in p:
        p = p.replace(old_row, new_row, 1)
        print("row ok")
    else:
        print("row miss")

    old_badge = """                      <span className={clsx('text-xs font-medium px-2 py-0.5 rounded border capitalize', statusStyles[t.status === 'new' ? 'open' : t.status] || statusStyles.open)}>
                        {(t.status === 'new' ? 'open' : t.status).replace('-', ' ')}
                      </span>"""
    new_badge = """                      <span className={clsx(
                        'text-xs font-medium px-2 py-0.5 rounded border capitalize',
                        statusStyles[
                          (sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                            ? 'closed'
                            : t.status === 'new'
                              ? 'open'
                              : t.status
                        ] || statusStyles.open
                      )}>
                        {((sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                          ? 'closed'
                          : t.status === 'new'
                            ? 'open'
                            : t.status
                        ).replace('-', ' ')}
                      </span>"""
    if old_badge in p:
        p = p.replace(old_badge, new_badge, 1)
        print("badge ok")
    else:
        print("badge miss")

    if '<option value="resolved">Resolved</option>' in p and 'value="closed"' not in p:
        p = p.replace(
            '<option value="resolved">Resolved</option>',
            '<option value="resolved">Resolved</option>\n            <option value="closed">Closed</option>',
            1,
        )
        print("filter ok")

    if "closed-sla-v1" not in p:
        p = "/* closed-sla-v1 */\n" + p
    tp.write_text(p)
    print("tp done")
else:
    print("tp already")

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "closed-sla-v1" not in d:
    if '<option value="resolved">Resolved</option>' in d and 'value="closed"' not in d:
        d = d.replace(
            '<option value="resolved">Resolved</option>',
            '<option value="resolved">Resolved</option>\n                <option value="closed">Closed</option>',
            1,
        )
        print("td option ok")
    if "closed-sla-v1" not in d:
        d = "/* closed-sla-v1 */\n" + d
    td.write_text(d)
    print("td done")
else:
    print("td already")

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "closed-sla-v1" not in c:
    c = c.replace(
        "    { id: 'track', label: 'Track Ticket', icon: Search },\n",
        "",
        1,
    )
    c = c.replace("setView('track');", "setView('mytickets');")
    c = c.replace(
        "Open Track Ticket or My Tickets anytime with your ID and account email.",
        "Open My Tickets anytime to follow status with your ticket ID and account email.",
    )
    c = c.replace(
        'under <span className="font-medium">Track Ticket</span> or <span className="font-medium">My Tickets</span>',
        'under <span className="font-medium">My Tickets</span>',
    )
    c = c.replace("Track Ticket", "My Tickets")
    if "closed-sla-v1" not in c:
        c = "/* closed-sla-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

css = """

/* closed-sla-v1 — red outline for SLA-breached / closed tickets */
.tickets-row-closed {
  box-shadow: inset 4px 0 0 0 #ef4444;
  background: rgba(239, 68, 68, 0.1);
}
html.nexus-dark .tickets-row-closed,
.dark .tickets-row-closed {
  background: rgba(239, 68, 68, 0.28) !important;
  box-shadow: inset 4px 0 0 0 #ef4444 !important;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "closed-sla-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
