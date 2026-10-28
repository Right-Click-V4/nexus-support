#!/usr/bin/env python3
"""Fix light-mode ticket detail + confirm contrast; redesign portal My Tickets table."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-table-v1" not in c:
    if "myTicketsPage" not in c:
        c = c.replace(
            "  const [view, setView] = useState<PortalView>('home');",
            """  const [view, setView] = useState<PortalView>('home');
  const [myTicketsPage, setMyTicketsPage] = useState(1);
  const [myTicketsDateFrom, setMyTicketsDateFrom] = useState('');
  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');""",
            1,
        )
        print("state ok")

    old_block = """            {view === 'mytickets' && (
              <div className="max-w-2xl">
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">My Tickets</h1>
                {myTickets.length === 0 ? (
                  <div className="rounded-xl border border-zinc-200 bg-white/80 px-4 py-3 text-sm text-zinc-500">No tickets linked to {user?.email} yet.</div>
                ) : (
                  <div className="space-y-2">
                    {myTickets.map((t) => (
                      <button key={t.id} type="button" onClick={() => { setTrackId(t.id); setTracked(t); setView('mytickets'); }} className="w-full text-left rounded-xl border border-zinc-200 bg-white/80 px-4 py-3 hover:border-violet-300 transition-colors">
                        <div className="flex justify-between gap-2">
                          <span className="font-mono text-xs text-zinc-400">{t.id}</span>
                          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${statusColor[t.status] || ''}`}>{t.status}</span>
                        </div>
                        <div className="font-medium text-zinc-900 mt-1">{t.title}</div>
                        <div className="text-xs text-zinc-500 mt-0.5">{t.branch || 'No branch'} · {new Date(t.created_at).toLocaleString()}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}"""

    new_block = """            {view === 'mytickets' && (() => {
              const PAGE_SIZE = 8;
              const filtered = myTickets.filter((t) => {
                if (myTicketsDateFrom) {
                  const from = new Date(myTicketsDateFrom);
                  from.setHours(0, 0, 0, 0);
                  if (new Date(t.created_at).getTime() < from.getTime()) return false;
                }
                if (myTicketsDateTo) {
                  const to = new Date(myTicketsDateTo);
                  to.setHours(23, 59, 59, 999);
                  if (new Date(t.created_at).getTime() > to.getTime()) return false;
                }
                return true;
              });
              const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
              const page = Math.min(myTicketsPage, totalPages);
              const slice = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
              return (
              <div className="max-w-5xl mx-auto w-full space-y-4">
                <div>
                  <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">My Tickets</h1>
                  <p className="mt-1.5 text-sm text-zinc-600 dark:text-zinc-300 max-w-2xl">
                    View and follow every support request linked to your account. Filter by date to find older tickets quickly.
                  </p>
                </div>

                <div className="portal-mytickets-panel rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-hidden">
                  <div className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 border-b border-zinc-200/70 dark:border-white/10">
                    <div className="text-xs font-medium text-zinc-500 dark:text-zinc-400">
                      {filtered.length} ticket{filtered.length !== 1 ? 's' : ''}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <label className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400">From</label>
                      <input
                        type="date"
                        value={myTicketsDateFrom}
                        onChange={(e) => { setMyTicketsDateFrom(e.target.value); setMyTicketsPage(1); }}
                        className="portal-mytickets-input text-xs rounded-lg px-2 py-1.5 border border-zinc-200 dark:border-white/15"
                      />
                      <label className="text-[11px] font-medium text-zinc-500 dark:text-zinc-400">To</label>
                      <input
                        type="date"
                        value={myTicketsDateTo}
                        onChange={(e) => { setMyTicketsDateTo(e.target.value); setMyTicketsPage(1); }}
                        className="portal-mytickets-input text-xs rounded-lg px-2 py-1.5 border border-zinc-200 dark:border-white/15"
                      />
                      {(myTicketsDateFrom || myTicketsDateTo) && (
                        <button
                          type="button"
                          onClick={() => { setMyTicketsDateFrom(''); setMyTicketsDateTo(''); setMyTicketsPage(1); }}
                          className="text-[11px] font-medium text-violet-600 dark:text-violet-300 hover:underline"
                        >
                          Clear
                        </button>
                      )}
                    </div>
                  </div>

                  {filtered.length === 0 ? (
                    <div className="px-4 py-10 text-center text-sm text-zinc-500 dark:text-zinc-400">
                      {myTickets.length === 0
                        ? `No tickets linked to ${user?.email || 'your account'} yet.`
                        : 'No tickets in this date range.'}
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="text-left text-[11px] uppercase tracking-wide text-zinc-500 dark:text-zinc-400 border-b border-zinc-200/70 dark:border-white/10">
                            <th className="px-4 py-2.5 font-semibold">ID</th>
                            <th className="px-4 py-2.5 font-semibold">Subject</th>
                            <th className="px-4 py-2.5 font-semibold">Branch</th>
                            <th className="px-4 py-2.5 font-semibold">Status</th>
                            <th className="px-4 py-2.5 font-semibold">Priority</th>
                            <th className="px-4 py-2.5 font-semibold">Submitted</th>
                          </tr>
                        </thead>
                        <tbody>
                          {slice.map((t) => (
                            <tr key={t.id} className="border-b border-zinc-100/80 dark:border-white/5 hover:bg-violet-500/5 transition-colors">
                              <td className="px-4 py-3 font-mono text-xs text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{t.id}</td>
                              <td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50 max-w-[220px]">
                                <div className="truncate" title={t.title}>{t.title}</div>
                              </td>
                              <td className="px-4 py-3 text-zinc-600 dark:text-zinc-300 whitespace-nowrap">{t.branch || '\u2014'}</td>
                              <td className="px-4 py-3">
                                <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${statusColor[t.status] || ''}`}>{t.status}</span>
                              </td>
                              <td className="px-4 py-3 capitalize text-zinc-700 dark:text-zinc-200">{t.priority}</td>
                              <td className="px-4 py-3 text-xs text-zinc-500 dark:text-zinc-400 whitespace-nowrap">
                                {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {filtered.length > 0 && (
                    <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 border-t border-zinc-200/70 dark:border-white/10">
                      <div className="text-xs text-zinc-500 dark:text-zinc-400">
                        Page {page} of {totalPages}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          disabled={page <= 1}
                          onClick={() => setMyTicketsPage((p) => Math.max(1, p - 1))}
                          className="px-3 py-1.5 text-xs font-medium rounded-lg border border-zinc-200 dark:border-white/15 text-zinc-700 dark:text-zinc-200 disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-white/5"
                        >
                          Previous
                        </button>
                        <button
                          type="button"
                          disabled={page >= totalPages}
                          onClick={() => setMyTicketsPage((p) => Math.min(totalPages, p + 1))}
                          className="px-3 py-1.5 text-xs font-medium rounded-lg border border-zinc-200 dark:border-white/15 text-zinc-700 dark:text-zinc-200 disabled:opacity-40 hover:bg-zinc-50 dark:hover:bg-white/5"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              );
            })()}"""

    if old_block in c:
        c = c.replace(old_block, new_block, 1)
        print("mytickets block ok")
    else:
        print("mytickets block miss")

    if "mytickets-table-v1" not in c:
        c = "/* mytickets-table-v1 */\n" + c
    cp.write_text(c)
    print("cp done")
else:
    print("cp already")

css = """

/* mytickets-table-v1 + light contrast fixes for ticket detail / confirm */
html.nexus-light .ticket-detail-page,
html:not(.nexus-dark):not(.dark) .ticket-detail-page {
  color: #0f172a !important;
}
html.nexus-light .ticket-detail-page .ticket-detail-panel,
html:not(.nexus-dark):not(.dark) .ticket-detail-page .ticket-detail-panel {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #e2e8f0 !important;
}
html.nexus-light .ticket-detail-page .ticket-detail-header,
html:not(.nexus-dark):not(.dark) .ticket-detail-page .ticket-detail-header {
  background: #f8fafc !important;
  border-color: #e2e8f0 !important;
}
html.nexus-light .ticket-detail-page h2,
html.nexus-light .ticket-detail-page .text-slate-900,
html.nexus-light .ticket-detail-page .text-slate-800,
html.nexus-light .ticket-detail-page .text-slate-700,
html:not(.nexus-dark):not(.dark) .ticket-detail-page h2 {
  color: #0f172a !important;
}
html.nexus-light .ticket-detail-page .text-slate-500,
html.nexus-light .ticket-detail-page .text-slate-400,
html.nexus-light .ticket-detail-page .text-slate-600 {
  color: #475569 !important;
}
html.nexus-light .ticket-detail-page .ticket-meta-block {
  background: #f1f5f9 !important;
  border-color: #e2e8f0 !important;
  color: #0f172a !important;
}

html.nexus-light .ticket-confirm-modal,
html:not(.nexus-dark):not(.dark) .ticket-confirm-modal {
  background: #ffffff !important;
  color: #0f172a !important;
  border-color: #e2e8f0 !important;
}
html.nexus-light .ticket-confirm-modal h3,
html:not(.nexus-dark):not(.dark) .ticket-confirm-modal h3 {
  color: #0f172a !important;
}
html.nexus-light .ticket-confirm-modal p,
html:not(.nexus-dark):not(.dark) .ticket-confirm-modal p {
  color: #334155 !important;
}

.portal-mytickets-panel {
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
html.nexus-dark .portal-mytickets-panel,
.dark .portal-mytickets-panel {
  background: rgba(24, 20, 42, 0.45);
  border-color: rgba(167, 139, 250, 0.2);
}
.portal-mytickets-input {
  background: rgba(255, 255, 255, 0.85);
  color: #0f172a;
}
html.nexus-dark .portal-mytickets-input,
.dark .portal-mytickets-input {
  background: rgba(15, 12, 30, 0.7);
  color: #f1f5f9;
  border-color: rgba(167, 139, 250, 0.25);
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "mytickets-table-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
