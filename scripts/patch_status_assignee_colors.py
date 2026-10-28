#!/usr/bin/env python3
"""Remove New status option; status row outline colors; assignee from live agents."""
from pathlib import Path

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "status-outline-v1" not in d:
    d = d.replace(
        """              <select value={status} onChange={(e) => setStatus(e.target.value as Status)} className="ticket-input w-full px-3 py-2 text-sm rounded-lg">
                <option value="new">New</option>
                <option value="open">Open</option>
                <option value="pending">Pending</option>
                <option value="on-hold">On Hold</option>
                <option value="resolved">Resolved</option>
              </select>""",
        """              <select
                value={status === 'new' ? 'open' : status}
                onChange={(e) => setStatus(e.target.value as Status)}
                className="ticket-input w-full px-3 py-2 text-sm rounded-lg"
              >
                <option value="open">Open</option>
                <option value="pending">Pending</option>
                <option value="on-hold">On Hold</option>
                <option value="resolved">Resolved</option>
              </select>""",
        1,
    )
    d = d.replace(
        """                {agents.map((a) => (
                  <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
                ))}""",
        """                {agents
                  .filter((a) => {
                    const st = (a.approval_status || 'approved').toLowerCase();
                    return st === 'approved' || st === '';
                  })
                  .map((a) => (
                  <option key={a.id} value={a.id}>{a.name}{a.is_admin ? ' (Admin)' : ''}</option>
                ))}""",
        1,
    )
    if "status-outline-v1" not in d:
        d = "/* status-outline-v1 */\n" + d
    td.write_text(d)
    print("td ok")
else:
    print("td already")

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "status-outline-v1" not in t:
    old = """                    className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      t.status === 'new' && t.channel === 'portal' && 'tickets-row-new-portal',
                      t.status === 'new' && t.channel !== 'portal' && 'tickets-row-new'
                    )}"""
    new = """                    className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      (t.status === 'open' || t.status === 'new') && 'tickets-row-open',
                      t.status === 'pending' && 'tickets-row-pending',
                      t.status === 'on-hold' && 'tickets-row-onhold',
                      t.status === 'resolved' && 'tickets-row-resolved',
                      ((t.tags || []).includes('unread') || t.status === 'new') && 'tickets-row-unread'
                    )}"""
    if old in t:
        t = t.replace(old, new, 1)
        print("row classes ok")
    else:
        print("row classes miss")
    if "status-outline-v1" not in t:
        t = "/* status-outline-v1 */\n" + t
    tp.write_text(t)
    print("tp ok")
else:
    print("tp already")

tc = Path("src/context/TicketContext.tsx")
if tc.exists():
    c = tc.read_text()
    if "status-outline-v1" not in c:
        old_f = """function filterAgents(list: Agent[]): Agent[] {
  const seen = new Set<string>();
  return list.filter((a) => {
    const role = (a.role || '').toLowerCase();
    if (role.includes('customer')) return false;
    if (a.approval_status === 'rejected') return false;
    const key = (a.email || a.name || a.id).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}"""
        new_f = """function filterAgents(list: Agent[]): Agent[] {
  const seen = new Set<string>();
  return list.filter((a) => {
    const role = (a.role || '').toLowerCase();
    if (role.includes('customer')) return false;
    const st = (a.approval_status || 'approved').toLowerCase();
    if (st === 'rejected' || st === 'pending') return false;
    const key = (a.email || a.name || a.id).toLowerCase();
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}"""
        if old_f in c:
            c = c.replace(old_f, new_f, 1)
            print("filterAgents ok")
        else:
            print("filterAgents miss")
        if "status-outline-v1" not in c:
            c = "// status-outline-v1\n" + c
        tc.write_text(c)
    else:
        print("tc already")

css = """

/* status-outline-v1 — ticket table row outlines by status */
.tickets-row-open {
  box-shadow: inset 3px 0 0 0 #3b82f6;
  background: rgba(59, 130, 246, 0.06);
}
.tickets-row-pending {
  box-shadow: inset 3px 0 0 0 #f97316;
  background: rgba(249, 115, 22, 0.07);
}
.tickets-row-onhold {
  box-shadow: inset 3px 0 0 0 #eab308;
  background: rgba(234, 179, 8, 0.08);
}
.tickets-row-resolved {
  box-shadow: inset 3px 0 0 0 #22c55e;
  background: rgba(34, 197, 94, 0.07);
}
html.nexus-dark .tickets-row-open,
.dark .tickets-row-open {
  background: rgba(59, 130, 246, 0.12);
  box-shadow: inset 3px 0 0 0 #60a5fa;
}
html.nexus-dark .tickets-row-pending,
.dark .tickets-row-pending {
  background: rgba(249, 115, 22, 0.12);
  box-shadow: inset 3px 0 0 0 #fb923c;
}
html.nexus-dark .tickets-row-onhold,
.dark .tickets-row-onhold {
  background: rgba(234, 179, 8, 0.12);
  box-shadow: inset 3px 0 0 0 #facc15;
}
html.nexus-dark .tickets-row-resolved,
.dark .tickets-row-resolved {
  background: rgba(34, 197, 94, 0.12);
  box-shadow: inset 3px 0 0 0 #4ade80;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "status-outline-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
