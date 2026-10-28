#!/usr/bin/env python3
"""Tickets table: 30 per page; assignee shows full first name."""
from pathlib import Path

p = Path("src/components/TicketsPage.tsx")
c = p.read_text()
if "tickets-page30-v1" in c:
    print("already")
    raise SystemExit(0)

if "const [ticketPage, setTicketPage]" not in c:
    for marker in [
        "  const [showCreate, setShowCreate] = useState(false);",
        "  const [confirmBusy, setConfirmBusy] = useState(false);",
    ]:
        if marker in c:
            c = c.replace(
                marker,
                marker + "\n  const [ticketPage, setTicketPage] = useState(1);",
                1,
            )
            print("page state ok")
            break
    else:
        print("page state miss")

if "const PAGE_SIZE = 30" not in c and "const pagedTickets" not in c:
    needle = "  const filtered = useMemo(() => {"
    if needle not in c:
        print("filtered miss")
    else:
        idx = c.find(needle)
        end = c.find("  }, [", idx)
        if end < 0:
            end = c.find("}, [", idx)
        endline = c.find("\n", end)
        insert_at = endline + 1
        block = """
  const PAGE_SIZE = 30;
  const totalTicketPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(ticketPage, totalTicketPages);
  const pagedTickets = useMemo(
    () => filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE),
    [filtered, safePage],
  );
  useEffect(() => {
    setTicketPage(1);
  }, [search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash]);
"""
        c = c[:insert_at] + block + c[insert_at:]
        print("paged ok")

c = c.replace("{filtered.map((t) => {", "{pagedTickets.map((t) => {", 1)

old_a = "{t.assignee?.initials || t.assignee?.name || '—'}"
new_a = "{(t.assignee?.name ? t.assignee.name.trim().split(/\\s+/)[0] : null) || t.assignee?.initials || '—'}"
if old_a in c:
    c = c.replace(old_a, new_a, 1)
    print("assignee ok")
else:
    print("assignee miss")

old_foot = """      <div className="text-xs text-slate-500">
        Showing {filtered.length} of {tickets.filter((t) => !!t.deleted_at === showTrash).length} tickets
      </div>"""
new_foot = """      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500">
        <span>
          Showing {filtered.length === 0 ? 0 : (safePage - 1) * PAGE_SIZE + 1}–{Math.min(safePage * PAGE_SIZE, filtered.length)} of {filtered.length} tickets
          {tickets.filter((t) => !!t.deleted_at === showTrash).length !== filtered.length
            ? ` (filtered from ${tickets.filter((t) => !!t.deleted_at === showTrash).length})`
            : ''}
        </span>
        <div className="flex items-center gap-2">
          <span className="tabular-nums">Page {safePage} of {totalTicketPages}</span>
          <button
            type="button"
            disabled={safePage <= 1}
            onClick={() => setTicketPage((p) => Math.max(1, p - 1))}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/15 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-white/5"
          >
            Previous
          </button>
          <button
            type="button"
            disabled={safePage >= totalTicketPages}
            onClick={() => setTicketPage((p) => Math.min(totalTicketPages, p + 1))}
            className="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-white/15 disabled:opacity-40 hover:bg-slate-50 dark:hover:bg-white/5"
          >
            Next
          </button>
        </div>
      </div>"""
if old_foot in c:
    c = c.replace(old_foot, new_foot, 1)
    print("footer ok")
else:
    print("footer miss")

if "tickets-page30-v1" not in c:
    c = "/* tickets-page30-v1 */\n" + c
p.write_text(c)
print("done")
