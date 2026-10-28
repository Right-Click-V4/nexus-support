#!/usr/bin/env python3
"""Replace ticket sidebar drawer with full Tickets-tab content panel + Back."""
from pathlib import Path
import re

td = Path("src/components/TicketDetail.tsx")
d = td.read_text()
if "ticket-panel-v1" in d:
    print("td already")
else:
    if "ArrowLeft" not in d:
        d = d.replace(
            "import { X, Trash2, MessageSquare, Clock, Paperclip, Download } from 'lucide-react';",
            "import { X, Trash2, MessageSquare, Clock, Paperclip, Download, ArrowLeft } from 'lucide-react';",
            1,
        )

    m = re.search(
        r"  return \(\n    <div className=\"fixed[^>]*>[\s\S]*?<div className=\"p-5 space-y-5\">",
        d,
    )
    if m:
        new_start = """  return (
    <div className="ticket-detail-page w-full max-w-5xl mx-auto space-y-4 pb-8">
      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={onClose}
          className="inline-flex items-center gap-1.5 text-sm font-medium px-3 py-2 rounded-lg border border-slate-200 dark:border-white/15 bg-white/80 dark:bg-white/5 text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-white/10 transition-colors"
        >
          <ArrowLeft size={16} />
          Back to Tickets
        </button>
        <div className="text-xs font-mono text-slate-500 dark:text-slate-400">{ticket.id}</div>
        {((ticket.tags || []).includes('unread') || ticket.status === 'new') && (
          <span className="ticket-new-badge text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded">New</span>
        )}
      </div>

      <div className="ticket-detail-panel rounded-2xl border border-slate-200 dark:border-white/10 shadow-sm overflow-hidden">
        <div className="ticket-detail-header px-5 sm:px-6 py-4 border-b flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-50 leading-tight tracking-tight">
              {ticket.title}
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
              Submitted {new Date(ticket.created_at).toLocaleString()}
              {ticket.channel ? ` · ${ticket.channel}` : ''}
            </p>
          </div>
        </div>

        <div className="p-5 sm:p-6 space-y-6">"""
        d = d[: m.start()] + new_start + d[m.end() :]
        print("shell replaced")
    else:
        print("shell miss")

    if "ticket-panel-v1" not in d:
        d = "/* ticket-panel-v1 */\n" + d
    td.write_text(d)
    print("td done")

tp = Path("src/components/TicketsPage.tsx")
t = tp.read_text()
if "ticket-panel-v1" in t:
    print("tp already")
else:
    t = t.replace(
        "const selected = selectedId ? tickets.find((t) => t.id === selectedId) : null;",
        """const selected = selectedId ? tickets.find((t) => t.id === selectedId) : null;

  if (selected) {
    return (
      <div className="space-y-4">
        <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />
      </div>
    );
  }""",
        1,
    )
    t = t.replace(
        "      {selected && <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />}\n",
        "",
        1,
    )
    if "ticket-panel-v1" not in t:
        t = "/* ticket-panel-v1 */\n" + t
    tp.write_text(t)
    print("tp done")

css = """

/* ticket-panel-v1 — full-page ticket detail under Tickets tab */
.ticket-detail-page .ticket-detail-panel {
  background: #ffffff;
  color: #0f172a;
}
html.nexus-dark .ticket-detail-page .ticket-detail-panel,
.dark .ticket-detail-page .ticket-detail-panel {
  background: rgba(24, 20, 42, 0.92);
  color: #f1f5f9;
  border-color: rgba(167, 139, 250, 0.22);
}
html.nexus-dark .ticket-detail-page .ticket-detail-header,
.dark .ticket-detail-page .ticket-detail-header {
  background: rgba(15, 12, 30, 0.6);
  border-color: rgba(167, 139, 250, 0.18);
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "ticket-panel-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
