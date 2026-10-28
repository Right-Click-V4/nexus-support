#!/usr/bin/env python3
"""Stronger light status colors; confirm delete/restore; 30-day trash purge; filter closed."""
from pathlib import Path
import re

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "trash-confirm-v1" not in t:
    if "confirmAction" not in t:
        t = t.replace(
            "  const [showTrash, setShowTrash] = useState(false);",
            """  const [showTrash, setShowTrash] = useState(false);
  const [confirmAction, setConfirmAction] = useState<{ type: 'delete' | 'restore'; id: string } | null>(null);
  const [confirmBusy, setConfirmBusy] = useState(false);""",
            1,
        )

    t = t.replace(
        """  const softDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Move this ticket to trash?')) return;
    await softDeleteTicket(id);
  };

  const restore = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await updateTicket(id, { deleted_at: null });
  };""",
        """  const softDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmAction({ type: 'delete', id });
  };

  const restore = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmAction({ type: 'restore', id });
  };

  const runConfirm = async () => {
    if (!confirmAction) return;
    setConfirmBusy(true);
    try {
      if (confirmAction.type === 'delete') {
        await softDeleteTicket(confirmAction.id);
      } else {
        await updateTicket(confirmAction.id, { deleted_at: null });
      }
      setConfirmAction(null);
    } catch (err) {
      console.error(err);
    } finally {
      setConfirmBusy(false);
    }
  };""",
        1,
    )

    old_f = "      if (statusFilter !== 'all' && t.status !== statusFilter) return false;"
    new_f = """      if (statusFilter !== 'all') {
        const slaTone = formatSlaCountdown(t.sla_due_at, t.status).tone;
        const isClosedView =
          t.status === 'closed' || (slaTone === 'breach' && t.status !== 'resolved');
        if (statusFilter === 'closed') {
          if (!isClosedView) return false;
        } else if (t.status === 'new' && statusFilter === 'open') {
          // ok
        } else if (t.status !== statusFilter) {
          if (!(t.status === 'new' && statusFilter === 'open')) return false;
        }
      }"""
    if old_f in t:
        t = t.replace(old_f, new_f, 1)
        print("filter closed ok")
    else:
        print("filter miss")

    modal = """
      {confirmAction && (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/50 p-4" onClick={() => !confirmBusy && setConfirmAction(null)}>
          <div
            className="ticket-confirm-modal w-full max-w-sm rounded-2xl border shadow-2xl px-6 py-6"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-50 mb-2">
              {confirmAction.type === 'delete' ? 'Move to trash?' : 'Restore ticket?'}
            </h3>
            <p className="text-sm text-slate-600 dark:text-slate-300 mb-5">
              {confirmAction.type === 'delete'
                ? 'This ticket will move to Trash. Items in Trash are permanently deleted after 30 days.'
                : 'This ticket will return to the active Tickets list.'}
            </p>
            <div className="flex gap-2 justify-end">
              <button
                type="button"
                disabled={confirmBusy}
                onClick={() => setConfirmAction(null)}
                className="px-4 py-2 text-sm font-medium rounded-lg border border-slate-200 dark:border-white/15 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-white/5 disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={confirmBusy}
                onClick={() => void runConfirm()}
                className={
                  confirmAction.type === 'delete'
                    ? 'px-4 py-2 text-sm font-medium rounded-lg bg-rose-600 text-white hover:bg-rose-700 disabled:opacity-50'
                    : 'px-4 py-2 text-sm font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50'
                }
              >
                {confirmBusy ? 'Please wait\u2026' : confirmAction.type === 'delete' ? 'Delete' : 'Restore'}
              </button>
            </div>
          </div>
        </div>
      )}
"""
    if "Move to trash?" not in t:
        if "{showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}" in t:
            t = t.replace(
                "{showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}",
                "{showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}" + modal,
                1,
            )
            print("modal ok")
        else:
            t = t.replace(
                "    </div>\n  );\n}",
                modal + "    </div>\n  );\n}",
                1,
            )
            print("modal fallback")

    if "trash-confirm-v1" not in t:
        t = "/* trash-confirm-v1 */\n" + t
    tp.write_text(t)
    print("tp done")
else:
    print("tp already")

tc = Path("src/context/TicketContext.tsx")
c = tc.read_text()
if "trash-confirm-v1" not in c:
    if "purgeExpiredTrash" not in c:
        insert = """
  const purgeExpiredTrash = async (list: Ticket[]) => {
    const cutoff = Date.now() - 30 * 24 * 60 * 60 * 1000;
    const expired = list.filter((t) => t.deleted_at && new Date(t.deleted_at).getTime() < cutoff);
    if (!expired.length) return;
    for (const t of expired) {
      try {
        if (supabase) {
          await supabase.from('tickets').delete().eq('id', t.id);
        }
      } catch (e) {
        console.warn('trash purge failed', t.id, e);
      }
    }
    if (expired.length) {
      setTickets((prev) => prev.filter((t) => !expired.some((e) => e.id === t.id)));
    }
  };

"""
        if "  const softDeleteTicket = async" in c:
            c = c.replace("  const softDeleteTicket = async", insert + "  const softDeleteTicket = async", 1)
            print("purge fn ok")
        if "purgeExpiredTrash(tickets)" not in c:
            effect = """
  useEffect(() => {
    if (!tickets.length) return;
    void purgeExpiredTrash(tickets);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tickets.length]);
"""
            marker = "  const softDeleteTicket = async (id: string) => {"
            if marker in c and "void purgeExpiredTrash(tickets)" not in c:
                c = c.replace(marker, effect + "\n" + marker, 1)
                print("purge effect ok")
            else:
                print("purge effect miss")

    if "trash-confirm-v1" not in c:
        c = "// trash-confirm-v1\n" + c
    tc.write_text(c)
    print("tc done")
else:
    print("tc already")

css = """

/* trash-confirm-v1 — stronger light-mode status colors + bolder outlines */
.tickets-row-open {
  box-shadow: inset 5px 0 0 0 #2563eb !important;
  background: rgba(37, 99, 235, 0.14) !important;
}
.tickets-row-pending {
  box-shadow: inset 5px 0 0 0 #ea580c !important;
  background: rgba(234, 88, 12, 0.16) !important;
}
.tickets-row-onhold {
  box-shadow: inset 5px 0 0 0 #ca8a04 !important;
  background: rgba(202, 138, 4, 0.18) !important;
}
.tickets-row-resolved {
  box-shadow: inset 5px 0 0 0 #16a34a !important;
  background: rgba(22, 163, 74, 0.14) !important;
}
.tickets-row-closed {
  box-shadow: inset 5px 0 0 0 #dc2626 !important;
  background: rgba(220, 38, 38, 0.16) !important;
}

.ticket-confirm-modal {
  background: #ffffff;
  border-color: #e2e8f0;
  color: #0f172a;
}
html.nexus-dark .ticket-confirm-modal,
.dark .ticket-confirm-modal {
  background: rgba(24, 20, 42, 0.98);
  border-color: rgba(167, 139, 250, 0.25);
  color: #f1f5f9;
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "trash-confirm-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
