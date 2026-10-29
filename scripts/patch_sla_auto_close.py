#!/usr/bin/env python3
"""Persist status=closed when SLA is breached (table + detail stay in sync)."""
from pathlib import Path

td = Path("src/components/TicketDetail.tsx")
c = td.read_text()
if "sla-auto-close-v1" in c:
    print("td already")
else:
    if "formatSlaCountdown" not in c:
        if "from '../lib/storage'" in c:
            c = c.replace(
                "import { uploadAttachment } from '../lib/storage';",
                "import { uploadAttachment } from '../lib/storage';\nimport { formatSlaCountdown } from '../lib/slaFormat';",
                1,
            )
        else:
            c = "import { formatSlaCountdown } from '../lib/slaFormat';\n" + c
        print("import sla ok")

    marker = """  /* Clear New/unread indicator when agent opens the ticket */
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
  }, [ticket.id]);"""

    insert = marker + """

  /* SLA breach \u2192 persist Closed so detail Status matches table */
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

    if marker in c:
        c = c.replace(marker, insert, 1)
        print("td effect ok")
    else:
        print("td marker miss")
    c = "/* sla-auto-close-v1 */\n" + c
    td.write_text(c)
    print("td done")

tp = Path("src/components/TicketsPage.tsx")
c = tp.read_text()
if "sla-auto-close-v1" in c:
    print("tp already")
else:
    anchor = None
    for a in [
        "  const [selectedId, setSelectedId] = useState<string | null>(null);",
        "  const [page, setPage] = useState(1);",
        "  const [showTrash, setShowTrash] = useState(false);",
    ]:
        if a in c:
            anchor = a
            break
    effect = """
  /* sla-batch-close: persist Closed for SLA-breached tickets (not resolved) */
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
  }, [tickets, updateTicket]);
"""
    if anchor:
        c = c.replace(anchor, anchor + "\n" + effect, 1)
        print("tp batch ok")
    else:
        print("tp anchor miss")
    c = "/* sla-auto-close-v1 */\n" + c
    tp.write_text(c)
    print("tp done")
print("done")
