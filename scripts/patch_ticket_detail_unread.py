#!/usr/bin/env python3
"""Ticket detail under topbar; new tickets status Open + unread New badge clears on open."""
from pathlib import Path

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "ticket-unread-v1" not in c:
    c = c.replace(
        """    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'new',
      channel: data.channel,
      assignee_id: autoAssignee,
      customer_name: data.customer_name,
      customer_email: data.customer_email || '',
      branch: data.branch?.trim() || undefined,
      tags,
      created_at: now,""",
        """    const ticket: Ticket = {
      id,
      title: data.title,
      description: data.description || '',
      priority,
      status: 'open',
      channel: data.channel,
      assignee_id: autoAssignee,
      customer_name: data.customer_name,
      customer_email: data.customer_email || '',
      branch: data.branch?.trim() || undefined,
      tags: Array.from(new Set([...(tags || []), 'unread'])),
      created_at: now,""",
        1,
    )
    if "ticket-unread-v1" not in c:
        c = "// ticket-unread-v1\n" + c
    tc.write_text(c)
    print("tc ok")
else:
    print("tc already")

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "ticket-unread-v1" not in d:
    if "useEffect" not in d.split("from 'react'")[0]:
        d = d.replace(
            "import { useMemo, useState, useRef } from 'react';",
            "import { useMemo, useState, useRef, useEffect } from 'react';",
            1,
        )

    insert_after = "  const isAdmin = !!currentAgent?.is_admin;"
    mark_read = """
  /* Clear New/unread indicator when agent opens the ticket */
  useEffect(() => {
    const tags = ticket.tags || [];
    const needs =
      tags.includes('unread') ||
      ticket.status === 'new';
    if (!needs) return;
    const nextTags = tags.filter((t) => t !== 'unread');
    void updateTicket(ticket.id, {
      ...(ticket.status === 'new' ? { status: 'open' as Status } : {}),
      tags: nextTags,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.id]);
"""
    if insert_after in d:
        d = d.replace(insert_after, insert_after + mark_read, 1)
        print("mark read ok")
    else:
        print("mark read miss")

    if 'fixed inset-0 z-50 flex justify-end' in d:
        d = d.replace(
            'fixed inset-0 z-50 flex justify-end bg-black/30',
            'fixed top-14 left-0 right-0 bottom-0 z-[70] flex justify-end bg-black/40',
            1,
        )
        print("overlay pos ok")
    else:
        print("overlay pos miss")

    if 'w-full max-w-md bg-white h-full shadow-xl' in d:
        d = d.replace(
            'w-full max-w-md bg-white h-full shadow-xl overflow-y-auto',
            'ticket-detail-panel w-full max-w-md h-full shadow-2xl overflow-y-auto border-l border-white/10',
            1,
        )
        print("panel class ok")

    if 'sticky top-0 bg-white border-b border-slate-200' in d:
        d = d.replace(
            'sticky top-0 bg-white border-b border-slate-200 px-5 py-4 flex items-center justify-between z-10',
            'sticky top-0 ticket-detail-header px-5 py-4 flex items-center justify-between z-10 border-b',
            1,
        )
        print("header class ok")

    if "ticket-unread-v1" not in d:
        d = "/* ticket-unread-v1 */\n" + d
    td.write_text(d)
    print("td done")
else:
    print("td already")

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "ticket-unread-v1" not in t:
    if 'tickets-subject' in t and 'ticket-new-badge' not in t:
        t = t.replace(
            '''                      <div className="tickets-subject truncate font-bold tracking-wide" title={t.title}>
                        {t.title}
                      </div>''',
            '''                      <div className="flex items-center gap-2 min-w-0">
                        <div className="tickets-subject truncate font-bold tracking-wide" title={t.title}>
                          {t.title}
                        </div>
                        {((t.tags || []).includes('unread') || t.status === 'new') && (
                          <span className="ticket-new-badge shrink-0 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded">
                            New
                          </span>
                        )}
                      </div>''',
            1,
        )
        print("new badge ok")
    else:
        print("new badge miss or exists")

    old_status = """                      <span className={clsx('text-xs font-medium px-2 py-0.5 rounded border capitalize', statusStyles[t.status])}>
                        {t.status.replace('-', ' ')}
                      </span>"""
    new_status = """                      <span className={clsx('text-xs font-medium px-2 py-0.5 rounded border capitalize', statusStyles[t.status === 'new' ? 'open' : t.status] || statusStyles.open)}>
                        {(t.status === 'new' ? 'open' : t.status).replace('-', ' ')}
                      </span>"""
    if old_status in t:
        t = t.replace(old_status, new_status, 1)
        print("status display ok")
    else:
        if "statusStyles[t.status]" in t and "t.status === 'new' ? 'open'" not in t:
            t = t.replace(
                "statusStyles[t.status]",
                "statusStyles[t.status === 'new' ? 'open' : t.status] || statusStyles.open",
                1,
            )
            t = t.replace(
                "{t.status.replace('-', ' ')}",
                "{(t.status === 'new' ? 'open' : t.status).replace('-', ' ')}",
                1,
            )
            print("status display loose ok")
        else:
            print("status display miss")

    if "ticket-unread-v1" not in t:
        t = "/* ticket-unread-v1 */\n" + t
    tp.write_text(t)
    print("tp done")
else:
    print("tp already")

css = """

/* ticket-unread-v1 — detail drawer under topbar + New badge */
.ticket-new-badge {
  background: rgba(16, 185, 129, 0.2);
  color: #059669;
  border: 1px solid rgba(16, 185, 129, 0.35);
}
html.nexus-dark .ticket-new-badge,
.dark .ticket-new-badge {
  background: rgba(52, 211, 153, 0.2);
  color: #6ee7b7;
  border-color: rgba(52, 211, 153, 0.4);
}
.ticket-detail-panel {
  background: #ffffff;
  color: #0f172a;
}
html.nexus-dark .ticket-detail-panel,
.dark .ticket-detail-panel {
  background: rgba(22, 18, 40, 0.98);
  color: #f1f5f9;
}
.ticket-detail-header {
  background: #ffffff;
  border-color: #e2e8f0;
}
html.nexus-dark .ticket-detail-header,
.dark .ticket-detail-header {
  background: rgba(15, 12, 30, 0.98);
  border-color: rgba(167, 139, 250, 0.2);
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "ticket-unread-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
