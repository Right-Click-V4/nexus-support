#!/usr/bin/env python3
"""Hide internal tags; Trash icon by Export; today stats; date filter."""
from pathlib import Path

p = Path("src/components/TicketsPage.tsx")
c = p.read_text()
if "tickets-ui-stats-v1" in c:
    print("already")
    raise SystemExit(0)

old_tags = """                      {(t.tags || []).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(t.tags || []).slice(0, 3).map((tag) => (
                            <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-normal">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}"""
if old_tags in c:
    c = c.replace(old_tags, "", 1)
    print("tags removed")
else:
    print("tags miss")

if "dateFilter" not in c:
    c = c.replace(
        "  const [showTrash, setShowTrash] = useState(false);",
        "  const [showTrash, setShowTrash] = useState(false);\n  const [dateFilter, setDateFilter] = useState(''); // YYYY-MM-DD local day filter",
        1,
    )
    print("dateFilter state")

if "const [, setTick]" in c:
    c = c.replace("const [, setTick] = useState(0);", "const [tick, setTick] = useState(0);", 1)
    print("tick var")

insert_after = """  useEffect(() => {
    const id = window.setInterval(() => setTick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);
"""
helpers = """  useEffect(() => {
    const id = window.setInterval(() => setTick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);

  const isSameLocalDay = (iso: string | undefined | null, dayKey: string) => {
    if (!iso || !dayKey) return false;
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return false;
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${y}-${m}-${day}` === dayKey;
  };

  const todayKey = useMemo(() => {
    const n = new Date();
    return `${n.getFullYear()}-${String(n.getMonth() + 1).padStart(2, '0')}-${String(n.getDate()).padStart(2, '0')}`;
  }, [tick]);

  const todayStats = useMemo(() => {
    const active = tickets.filter((t) => !t.deleted_at);
    const onDay = active.filter((t) => isSameLocalDay(t.updated_at || t.created_at, todayKey));
    return {
      resolved: onDay.filter((t) => t.status === 'resolved').length,
      pending: onDay.filter((t) => t.status === 'pending').length,
      onHold: onDay.filter((t) => t.status === 'on-hold').length,
      closed: onDay.filter(
        (t) =>
          t.status === 'closed' ||
          (formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach' && t.status !== 'resolved'),
      ).length,
    };
  }, [tickets, todayKey]);
"""
if "todayStats" not in c and insert_after in c:
    c = c.replace(insert_after, helpers, 1)
    print("todayStats ok")
elif "todayStats" in c:
    print("todayStats already")
else:
    print("todayStats miss")

old_ret = """      if (search) {
        const q = search.toLowerCase();
        const tagHit = (t.tags || []).some((tag) => tag.toLowerCase().includes(q));
        if (
          !t.title.toLowerCase().includes(q) &&
          !t.id.toLowerCase().includes(q) &&
          !t.customer_name.toLowerCase().includes(q) &&
          !(t.branch || '').toLowerCase().includes(q) &&
          !(t.customer_email || '').toLowerCase().includes(q) &&
          !tagHit
        )
          return false;
      }
      return true;
    });
  }, [tickets, search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash]);"""

new_ret = """      if (dateFilter) {
        const dayHit =
          isSameLocalDay(t.created_at, dateFilter) || isSameLocalDay(t.updated_at, dateFilter);
        if (!dayHit) return false;
      }
      if (search) {
        const q = search.toLowerCase();
        if (
          !t.title.toLowerCase().includes(q) &&
          !t.id.toLowerCase().includes(q) &&
          !t.customer_name.toLowerCase().includes(q) &&
          !(t.branch || '').toLowerCase().includes(q) &&
          !(t.customer_email || '').toLowerCase().includes(q)
        )
          return false;
      }
      return true;
    });
  }, [tickets, search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash, dateFilter]);"""

if old_ret in c:
    c = c.replace(old_ret, new_ret, 1)
    print("filter date ok")
else:
    print("filter date miss")

c = c.replace(
    "  }, [search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash]);",
    "  }, [search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash, dateFilter]);",
    1,
)

old_toolbar = """        <button
          type="button"
          onClick={() => setShowTrash((v) => !v)}
          className={clsx(
            'text-sm px-3 py-2 rounded-lg border',
            showTrash ? 'bg-rose-50 border-rose-200 text-rose-700' : 'bg-white border-slate-200 text-slate-600'
          )}
        >
          Trash
        </button>
        <div className="flex-1" />
        <button
          type="button"
          onClick={exportCsv}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-2 border border-slate-200 rounded-lg bg-white text-slate-600 hover:bg-slate-50"
        >
          <Download size={16} /> Export
        </button>
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 font-medium"
        >
          <Plus size={16} /> New ticket
        </button>
      </div>"""

new_toolbar = """        <input
          type="date"
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
          className="text-sm border border-slate-200 dark:border-white/15 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-slate-800 dark:text-slate-100"
          title="Filter by date"
        />
        {dateFilter && (
          <button
            type="button"
            onClick={() => setDateFilter('')}
            className="text-xs px-2 py-2 rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50"
          >
            Clear date
          </button>
        )}
        <div className="flex-1" />
        <button
          type="button"
          onClick={exportCsv}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-2 border border-slate-200 rounded-lg bg-white text-slate-600 hover:bg-slate-50"
        >
          <Download size={16} /> Export
        </button>
        <button
          type="button"
          onClick={() => setShowTrash((v) => !v)}
          className={clsx(
            'inline-flex items-center justify-center p-2 rounded-lg border',
            showTrash
              ? 'bg-rose-50 border-rose-200 text-rose-700'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
          )}
          title={showTrash ? 'Back to tickets' : 'Trash'}
          aria-label="Trash"
        >
          <Trash2 size={16} />
        </button>
        <button
          type="button"
          onClick={() => setShowCreate(true)}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 font-medium"
        >
          <Plus size={16} /> New ticket
        </button>
      </div>

      {!showTrash && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {(
            [
              { key: 'resolved', label: 'Resolved today', value: todayStats.resolved, color: 'text-emerald-600 bg-emerald-50 border-emerald-200' },
              { key: 'pending', label: 'Pending today', value: todayStats.pending, color: 'text-orange-600 bg-orange-50 border-orange-200' },
              { key: 'onHold', label: 'On hold today', value: todayStats.onHold, color: 'text-amber-700 bg-amber-50 border-amber-200' },
              { key: 'closed', label: 'Closed today', value: todayStats.closed, color: 'text-rose-600 bg-rose-50 border-rose-200' },
            ] as const
          ).map((s) => (
            <div
              key={s.key}
              className={clsx('rounded-xl border px-3 py-2.5 flex flex-col gap-0.5', s.color)}
            >
              <span className="text-[10px] font-semibold uppercase tracking-wide opacity-80">{s.label}</span>
              <span className="text-xl font-bold tabular-nums leading-none">{s.value}</span>
            </div>
          ))}
        </div>
      )}"""

if old_toolbar in c:
    c = c.replace(old_toolbar, new_toolbar, 1)
    print("toolbar ok")
else:
    print("toolbar miss")

c = "/* tickets-ui-stats-v1 */\n" + c
p.write_text(c)
print("done")
