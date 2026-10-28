#!/usr/bin/env python3
"""My Tickets: left table + right status guidelines panel."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "mytickets-guide-v1" in c:
    print("already")
    raise SystemExit(0)

start = c.find("            {view === 'mytickets' && (() => {")
end = c.find("            {view === 'help' && (", start)
if start < 0 or end < 0:
    print("block miss", start, end)
    raise SystemExit(1)

new_block = r'''            {view === 'mytickets' && (() => {
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
              const statusGuide = [
                { key: 'open', label: 'Open', color: 'bg-amber-100 text-amber-800 dark:bg-amber-500/20 dark:text-amber-200', meaning: 'Your ticket was received and is waiting in the queue for an agent to pick it up.' },
                { key: 'pending', label: 'Pending', color: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200', meaning: 'An agent or tech support is actively working on your ticket and following up.' },
                { key: 'on-hold', label: 'On Hold', color: 'bg-zinc-200 text-zinc-700 dark:bg-zinc-500/30 dark:text-zinc-200', meaning: 'Work is paused \u2014 often waiting on more details from you or a third party.' },
                { key: 'resolved', label: 'Resolved', color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/20 dark:text-emerald-200', meaning: 'The issue was addressed. You can still reply if something is still wrong.' },
                { key: 'closed', label: 'Closed', color: 'bg-rose-100 text-rose-800 dark:bg-rose-500/20 dark:text-rose-200', meaning: 'The ticket is closed (for example past SLA or fully completed). Contact support if you need it reopened.' },
                { key: 'new', label: 'New', color: 'bg-sky-100 text-sky-800 dark:bg-sky-500/20 dark:text-sky-200', meaning: 'Just submitted and not yet reviewed \u2014 it will move to Open or Pending soon.' },
              ];
              return (
              <div className="w-full max-w-6xl space-y-4">
                <div>
                  <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">My Tickets</h1>
                  <p className="mt-1.5 text-sm text-zinc-600 dark:text-zinc-300 max-w-2xl">
                    View and follow every support request linked to your account. Filter by date to find older tickets quickly.
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
                  <div className="lg:col-span-8 portal-mytickets-panel rounded-2xl border border-zinc-200/80 dark:border-white/10 overflow-hidden">
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
                              <td className="px-4 py-3 font-medium text-zinc-900 dark:text-zinc-50 max-w-[200px]">
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

                  <aside className="lg:col-span-4 portal-mytickets-guide rounded-2xl border border-zinc-200/80 dark:border-white/10 p-4 sm:p-5 space-y-3">
                    <div>
                      <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Status guidelines</h2>
                      <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
                        What each status means for your ticket.
                      </p>
                    </div>
                    <ul className="space-y-3">
                      {statusGuide.map((s) => (
                        <li key={s.key} className="flex gap-3">
                          <span className={`mt-0.5 shrink-0 text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${s.color}`}>{s.label}</span>
                          <p className="text-xs text-zinc-600 dark:text-zinc-300 leading-relaxed">{s.meaning}</p>
                        </li>
                      ))}
                    </ul>
                  </aside>
                </div>
              </div>
              );
            })()}

'''

c = c[:start] + new_block + c[end:]
if "mytickets-guide-v1" not in c:
    c = "/* mytickets-guide-v1 */\n" + c
cp.write_text(c)
print("cp done")

css = """

/* mytickets-guide-v1 — status guide panel */
.portal-mytickets-guide {
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
html.nexus-dark .portal-mytickets-guide,
.dark .portal-mytickets-guide {
  background: rgba(24, 20, 42, 0.45);
  border-color: rgba(167, 139, 250, 0.2);
}
"""

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "mytickets-guide-v1" in x:
        print(f"{path.name}: already")
        continue
    path.write_text(x + css)
    print(f"{path.name}: css ok")

print("done")
