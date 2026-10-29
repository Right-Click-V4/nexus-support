#!/usr/bin/env python3
"""Fix SLA auto-close race: don't reset Status back to On Hold."""
from pathlib import Path

td = Path("src/components/TicketDetail.tsx")
c = td.read_text()
if "sla-close-race-v1" in c:
    print("td already")
else:
    old = """  /* SLA breach \u2192 persist Closed so detail Status matches table */
  useEffect(() => {
    if (ticket.status === 'resolved' || ticket.status === 'closed') return;
    const sla = formatSlaCountdown(ticket.sla_due_at, ticket.status);
    if (sla.tone !== 'breach') return;
    setStatus('closed');
    void updateTicket(ticket.id, { status: 'closed' as Status });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.id, ticket.sla_due_at, ticket.status]);

  /* Keep local form fields in sync when ticket updates from outside */
  useEffect(() => {
    setStatus(ticket.status);
    setPriority(ticket.priority);
    setAssigneeId(ticket.assignee_id || '');
    setBranch(ticket.branch || '');
    setResolutionPlan(planFromTags(ticket.tags));
    setResolutionOther(planNoteFromTags(ticket.tags));
  }, [ticket.id, ticket.status, ticket.priority, ticket.assignee_id, ticket.branch, ticket.tags]);"""
    old = old.replace("\\u2192", "\u2192")
    new = """  /* SLA breach \u2192 persist Closed; sync form without undoing auto-close */
  useEffect(() => {
    const breached =
      ticket.status !== 'resolved' &&
      ticket.status !== 'closed' &&
      formatSlaCountdown(ticket.sla_due_at, ticket.status).tone === 'breach';

    if (breached) {
      setStatus('closed');
      void updateTicket(ticket.id, { status: 'closed' as Status });
    } else {
      setStatus(ticket.status);
    }
    setPriority(ticket.priority);
    setAssigneeId(ticket.assignee_id || '');
    setBranch(ticket.branch || '');
    setResolutionPlan(planFromTags(ticket.tags));
    setResolutionOther(planNoteFromTags(ticket.tags));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ticket.id, ticket.sla_due_at, ticket.status, ticket.priority, ticket.assignee_id, ticket.branch, ticket.tags]);""".replace("\\u2192", "\u2192")

    if old in c:
        c = c.replace(old, new, 1)
        print("race fixed")
    else:
        # flexible: match without special arrow
        import re
        m = re.search(
            r"  /\* SLA breach.*?persist Closed so detail Status matches table \*/\s*useEffect\([\s\S]*?\}, \[ticket\.id, ticket\.sla_due_at, ticket\.status\]\);\s*/\* Keep local form fields[\s\S]*?\}, \[ticket\.id, ticket\.status, ticket\.priority, ticket\.assignee_id, ticket\.branch, ticket\.tags\]\);",
            c,
        )
        if m:
            c = c[: m.start()] + new + c[m.end() :]
            print("race fixed re")
        else:
            print("marker miss")
    c = "/* sla-close-race-v1 */\n" + c
    td.write_text(c)
    print("td done")

tp = Path("src/components/TicketsPage.tsx")
c = tp.read_text()
if "sla-close-race-v1" in c:
    print("tp already")
else:
    old = """  /* sla-batch-close: persist Closed for SLA-breached tickets (not resolved) */
  useEffect(() => {
    const breached = tickets.filter(
      (t) =>
        !t.deleted_at &&
        t.status !== 'resolved' &&
        t.status !== 'closed' &&
        formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach'
    );
    if (!breached.length) return;
    for (const t of breached.slice(0, 25)) {
      void updateTicket(t.id, { status: 'closed' });
    }
  }, [tickets, updateTicket]);"""
    new = """  /* sla-batch-close: persist Closed for SLA-breached tickets (not resolved) */
  const closedBreachRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    const breached = tickets.filter(
      (t) =>
        !t.deleted_at &&
        t.status !== 'resolved' &&
        t.status !== 'closed' &&
        formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach' &&
        !closedBreachRef.current.has(t.id)
    );
    if (!breached.length) return;
    for (const t of breached.slice(0, 25)) {
      closedBreachRef.current.add(t.id);
      void updateTicket(t.id, { status: 'closed' });
    }
  }, [tickets, updateTicket]);"""
    if old in c:
        c = c.replace(old, new, 1)
        print("tp batch ok")
    else:
        print("tp batch miss")
    if "useRef" not in c[:500]:
        c = c.replace(
            "import { useEffect, useMemo, useState } from 'react';",
            "import { useEffect, useMemo, useRef, useState } from 'react';",
            1,
        )
        print("useRef import")
    c = "/* sla-close-race-v1 */\n" + c
    tp.write_text(c)
    print("tp done")
print("done")
