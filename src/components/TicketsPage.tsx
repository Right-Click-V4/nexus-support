/* tickets-ui-stats-v1 */
/* sla-close-race-v1 */
/* sla-auto-close-v1 */
/* tickets-page30-v1 */
/* trash-confirm-v1 */
/* closed-sla-v1 */
/* status-outline-v1 */
/* ticket-panel-v1 */
/* ticket-unread-v1 */
/* details-tickets-theme-v1 */
/* tickets-table-v2 */
/* badges-dark-v1 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Plus, Search, Download, Trash2, RotateCcw } from 'lucide-react';
import clsx from 'clsx';
import { useTickets } from '../context/TicketContext';
import type { Priority, Status } from '../types';
import { formatSlaCountdown } from '../lib/slaFormat';
import CreateTicketModal from './CreateTicketModal';
import TicketDetail from './TicketDetail';

const priorityStyles: Record<string, string> = {
  critical:
    'bg-rose-100 text-rose-800 ring-1 ring-inset ring-rose-200/90 dark:bg-rose-500/15 dark:text-rose-300 dark:ring-rose-400/35',
  high:
    'bg-orange-100 text-orange-800 ring-1 ring-inset ring-orange-200/90 dark:bg-orange-500/15 dark:text-orange-300 dark:ring-orange-400/35',
  medium:
    'bg-violet-100 text-violet-800 ring-1 ring-inset ring-violet-200/90 dark:bg-violet-500/15 dark:text-violet-300 dark:ring-violet-400/35',
  low:
    'bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-200/90 dark:bg-white/8 dark:text-slate-300 dark:ring-white/15',
};

const statusStyles: Record<string, string> = {
  new: 'bg-sky-50 text-sky-800 border-sky-200 dark:bg-sky-500/15 dark:text-sky-300 dark:border-sky-400/30',
  open: 'bg-amber-50 text-amber-800 border-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-400/30',
  pending: 'bg-violet-50 text-violet-800 border-violet-200 dark:bg-violet-500/15 dark:text-violet-300 dark:border-violet-400/30',
  resolved: 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-500/15 dark:text-emerald-300 dark:border-emerald-400/30',
  'on-hold': 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-white/8 dark:text-slate-300 dark:border-white/15',
  closed: 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:border-rose-400/30',
};

/** Channel pills — readable in light + dark */
const channelStyles: Record<string, string> = {
  portal:
    'bg-violet-100 text-violet-800 ring-1 ring-inset ring-violet-200/90 dark:bg-violet-500/20 dark:text-violet-200 dark:ring-violet-400/40',
  email:
    'bg-sky-100 text-sky-800 ring-1 ring-inset ring-sky-200/90 dark:bg-sky-500/20 dark:text-sky-200 dark:ring-sky-400/40',
  chat:
    'bg-fuchsia-100 text-fuchsia-800 ring-1 ring-inset ring-fuchsia-200/90 dark:bg-fuchsia-500/20 dark:text-fuchsia-200 dark:ring-fuchsia-400/40',
  phone:
    'bg-amber-100 text-amber-900 ring-1 ring-inset ring-amber-200/90 dark:bg-amber-500/20 dark:text-amber-200 dark:ring-amber-400/40',
};
const channelFallback =
  'bg-slate-100 text-slate-700 ring-1 ring-inset ring-slate-200/90 dark:bg-white/10 dark:text-slate-300 dark:ring-white/15';

export default function TicketsPage() {
  const { tickets, loading, updateTicket, softDeleteTicket } = useTickets();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<Status | 'all'>('all');
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');
  const [channelFilter, setChannelFilter] = useState<'all' | 'portal' | 'email' | 'chat' | 'phone'>('all');
  const [slaFilter, setSlaFilter] = useState<'all' | 'breach' | 'warn'>('all');
  const [showTrash, setShowTrash] = useState(false);
  const [dateFilter, setDateFilter] = useState('');
  const [confirmAction, setConfirmAction] = useState<{ type: 'delete' | 'restore'; id: string } | null>(null);
  const [confirmBusy, setConfirmBusy] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [ticketPage, setTicketPage] = useState(1);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const closedBreachRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    const breached = tickets.filter(
      (t) =>
        !t.deleted_at &&
        t.status !== 'resolved' &&
        t.status !== 'closed' &&
        formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach' &&
        !closedBreachRef.current.has(t.id),
    );
    if (!breached.length) return;
    for (const t of breached.slice(0, 25)) {
      closedBreachRef.current.add(t.id);
      void updateTicket(t.id, { status: 'closed' });
    }
  }, [tickets, updateTicket]);

  const [tick, setTick] = useState(0);
  useEffect(() => {
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

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      const isDeleted = !!t.deleted_at;
      if (showTrash ? !isDeleted : isDeleted) return false;
      if (statusFilter !== 'all') {
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
      }
      if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;
      if (channelFilter !== 'all' && t.channel !== channelFilter) return false;
      if (slaFilter !== 'all') {
        const sla = formatSlaCountdown(t.sla_due_at, t.status);
        if (slaFilter === 'breach' && sla.tone !== 'breach') return false;
        if (slaFilter === 'warn' && sla.tone !== 'warn' && sla.tone !== 'breach') return false;
      }
      if (dateFilter) {
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
  }, [tickets, search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash, dateFilter]);

  const PAGE_SIZE = 30;
  const totalTicketPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(ticketPage, totalTicketPages);
  const pagedTickets = useMemo(
    () => filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE),
    [filtered, safePage],
  );
  useEffect(() => {
    setTicketPage(1);
  }, [search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash, dateFilter]);

  const selected = selectedId ? tickets.find((t) => t.id === selectedId) : null;

  if (selected) {
    return (
      <div className="space-y-4">
        <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />
      </div>
    );
  }
  const breachCount = tickets.filter(
    (t) => !t.deleted_at && t.status !== 'resolved' && formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach',
  ).length;

  const exportCsv = () => {
    const headers = ['ID', 'Title', 'Customer', 'Email', 'Branch', 'Tags', 'Priority', 'Status', 'Channel', 'Assignee', 'SLA due', 'Created'];
    const rows = filtered.map((t) => [
      t.id,
      `"${t.title.replace(/"/g, '""')}"`,
      `"${t.customer_name.replace(/"/g, '""')}"`,
      t.customer_email || '',
      t.branch || '',
      `"${(t.tags || []).join('; ')}"`,
      t.priority,
      t.status,
      t.channel,
      t.assignee?.name || '',
      t.sla_due_at || '',
      t.created_at,
    ]);
    const csv = [headers.join(','), ...rows.map((r) => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'nexus-tickets.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const softDelete = (id: string, e: React.MouseEvent) => {
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
  };

  return (
    <div className="space-y-4">
      {breachCount > 0 && (
        <button
          type="button"
          onClick={() => setSlaFilter('breach')}
          className="w-full text-left rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900 dark:bg-rose-500/15 dark:border-rose-400/30 dark:text-rose-200"
        >
          <strong>{breachCount} ticket{breachCount !== 1 ? 's' : ''}</strong> past SLA — click to filter breached.
        </button>
      )}

      <div className="flex flex-wrap items-center gap-3">
        <div className="relative flex-1 min-w-[200px] max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tickets, tags, customers..."
            className="w-full pl-9 pr-3 py-2 text-sm bg-white dark:bg-white/5 border border-slate-200 dark:border-white/15 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/30 text-slate-800 dark:text-slate-100"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as Status | 'all')}
          className="text-sm border border-slate-200 dark:border-white/15 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-slate-800 dark:text-slate-100"
        >
          <option value="all">All statuses</option>
          <option value="new">New</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="on-hold">On hold</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as Priority | 'all')}
          className="text-sm border border-slate-200 dark:border-white/15 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-slate-800 dark:text-slate-100"
        >
          <option value="all">All priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={channelFilter}
          onChange={(e) => setChannelFilter(e.target.value as typeof channelFilter)}
          className="text-sm px-3 py-2 border border-slate-200 dark:border-white/15 rounded-lg bg-white dark:bg-zinc-900 text-slate-800 dark:text-slate-100"
        >
          <option value="all">All channels</option>
          <option value="portal">Portal</option>
          <option value="email">Email</option>
          <option value="chat">Chat</option>
          <option value="phone">Phone</option>
        </select>
        <select
          value={slaFilter}
          onChange={(e) => setSlaFilter(e.target.value as 'all' | 'breach' | 'warn')}
          className="text-sm border border-slate-200 dark:border-white/15 rounded-lg px-3 py-2 bg-white dark:bg-zinc-900 text-slate-800 dark:text-slate-100"
        >
          <option value="all">All SLA</option>
          <option value="warn">At risk</option>
          <option value="breach">Breached</option>
        </select>
        <input
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
            className="text-xs px-2 py-2 rounded-lg border border-slate-200 dark:border-white/15 text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/5"
          >
            Clear date
          </button>
        )}
        <div className="flex-1" />
        <button
          type="button"
          onClick={exportCsv}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-2 border border-slate-200 dark:border-white/15 rounded-lg bg-white dark:bg-white/5 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/10"
        >
          <Download size={16} /> Export
        </button>
        <button
          type="button"
          onClick={() => setShowTrash((v) => !v)}
          className={clsx(
            'inline-flex items-center justify-center p-2 rounded-lg border',
            showTrash
              ? 'bg-rose-50 border-rose-200 text-rose-700 dark:bg-rose-500/15 dark:border-rose-400/30 dark:text-rose-300'
              : 'bg-white dark:bg-white/5 border-slate-200 dark:border-white/15 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/10',
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
              { key: 'resolved', label: 'Resolved today', value: todayStats.resolved, color: 'text-emerald-700 bg-emerald-50 border-emerald-200 dark:text-emerald-300 dark:bg-emerald-500/15 dark:border-emerald-400/25' },
              { key: 'pending', label: 'Pending today', value: todayStats.pending, color: 'text-orange-700 bg-orange-50 border-orange-200 dark:text-orange-300 dark:bg-orange-500/15 dark:border-orange-400/25' },
              { key: 'onHold', label: 'On hold today', value: todayStats.onHold, color: 'text-amber-800 bg-amber-50 border-amber-200 dark:text-amber-300 dark:bg-amber-500/15 dark:border-amber-400/25' },
              { key: 'closed', label: 'Closed today', value: todayStats.closed, color: 'text-rose-700 bg-rose-50 border-rose-200 dark:text-rose-300 dark:bg-rose-500/15 dark:border-rose-400/25' },
            ] as const
          ).map((s) => (
            <div key={s.key} className={clsx('rounded-xl border px-3 py-2.5 flex flex-col gap-0.5', s.color)}>
              <span className="text-[10px] font-semibold uppercase tracking-wide opacity-80">{s.label}</span>
              <span className="text-xl font-bold tabular-nums leading-none">{s.value}</span>
            </div>
          ))}
        </div>
      )}

      <div className="tickets-table-panel rounded-xl border shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-10 text-center tickets-muted text-sm">Loading tickets...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="tickets-table-head border-b">
              <tr className="text-left">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Subject</th>
                <th className="px-4 py-3 font-medium">Customer</th>
                <th className="px-4 py-3 font-medium">Branch</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">SLA</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Submitted</th>
                <th className="px-4 py-3 font-medium">Assignee</th>
                <th className="px-4 py-3 font-medium w-20"></th>
              </tr>
            </thead>
            <tbody>
              {pagedTickets.map((t) => {
                const sla = formatSlaCountdown(t.sla_due_at, t.status);
                return (
                  <tr
                    key={t.id}
                    onClick={() => setSelectedId(t.id)}
                    className={clsx(
                      'tickets-row border-b cursor-pointer transition-colors',
                      (sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                        ? 'tickets-row-closed'
                        : clsx(
                            (t.status === 'open' || t.status === 'new') && 'tickets-row-open',
                            t.status === 'pending' && 'tickets-row-pending',
                            t.status === 'on-hold' && 'tickets-row-onhold',
                            t.status === 'resolved' && 'tickets-row-resolved',
                          ),
                      ((t.tags || []).includes('unread') || t.status === 'new') && 'tickets-row-unread',
                    )}
                  >
                    <td className="px-4 py-3 font-mono text-xs tickets-muted">{t.id}</td>
                    <td className="px-4 py-3 max-w-[240px]">
                      <div className="flex items-center gap-2 min-w-0">
                        <div className="tickets-subject truncate font-bold tracking-wide" title={t.title}>
                          {t.title}
                        </div>
                        {((t.tags || []).includes('unread') || t.status === 'new') && (
                          <span className="ticket-new-badge shrink-0 text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded">
                            New
                          </span>
                        )}
                      </div>
                      {t.description ? (
                        <div className="tickets-desc text-[11px] truncate mt-0.5 font-normal" title={t.description}>
                          {t.description}
                        </div>
                      ) : null}
                    </td>
                    <td className="px-4 py-3">
                      <div className="tickets-cell font-medium">{t.customer_name}</div>
                      {t.customer_email && (
                        <div className="text-[11px] tickets-muted truncate max-w-[140px]">{t.customer_email}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 tickets-cell text-xs max-w-[120px] truncate" title={t.branch || ''}>
                      {t.branch || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'inline-flex items-center text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md',
                          priorityStyles[t.priority] || priorityStyles.low,
                        )}
                      >
                        {t.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'inline-flex items-center text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md border capitalize',
                          statusStyles[
                            (sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                              ? 'closed'
                              : t.status === 'new'
                                ? 'open'
                                : t.status
                          ] || statusStyles.open,
                        )}
                      >
                        {((sla.tone === 'breach' && t.status !== 'resolved') || t.status === 'closed'
                          ? 'closed'
                          : t.status === 'new'
                            ? 'open'
                            : t.status
                        ).replace('-', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'inline-flex items-center text-[10px] font-semibold tabular-nums tracking-wide px-2 py-0.5 rounded-md',
                          sla.tone === 'breach' &&
                            'bg-rose-100 text-rose-800 ring-1 ring-inset ring-rose-200/90 dark:bg-rose-500/20 dark:text-rose-300 dark:ring-rose-400/35',
                          sla.tone === 'warn' &&
                            'bg-amber-100 text-amber-900 ring-1 ring-inset ring-amber-200/90 dark:bg-amber-500/20 dark:text-amber-300 dark:ring-amber-400/35',
                          sla.tone === 'ok' &&
                            'bg-emerald-50 text-emerald-800 ring-1 ring-inset ring-emerald-200/90 dark:bg-emerald-500/15 dark:text-emerald-300 dark:ring-emerald-400/30',
                          sla.tone === 'done' && 'text-slate-500 dark:text-slate-400',
                        )}
                        title={t.sla_due_at ? new Date(t.sla_due_at).toLocaleString() : 'No SLA'}
                      >
                        {sla.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'inline-flex items-center text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md',
                          channelStyles[String(t.channel || '').toLowerCase()] || channelFallback,
                        )}
                      >
                        {t.channel || '—'}
                      </span>
                    </td>
                    <td
                      className="px-4 py-3 text-[11px] tickets-muted whitespace-nowrap tabular-nums"
                      title={new Date(t.created_at).toLocaleString()}
                    >
                      {new Date(t.created_at).toLocaleString(undefined, {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td className="px-4 py-3 tickets-cell">
                      {(t.assignee?.name ? t.assignee.name.trim().split(/\s+/)[0] : null) ||
                        t.assignee?.initials ||
                        '—'}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {showTrash ? (
                        <button
                          type="button"
                          onClick={(e) => void restore(t.id, e)}
                          className="p-1.5 text-slate-400 hover:text-emerald-600 dark:hover:text-emerald-400"
                          title="Restore"
                        >
                          <RotateCcw size={14} />
                        </button>
                      ) : (
                        <button
                          type="button"
                          onClick={(e) => void softDelete(t.id, e)}
                          className="p-1.5 text-slate-400 hover:text-rose-600 dark:hover:text-rose-400"
                          title="Trash"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
        {!loading && filtered.length === 0 && (
          <div className="p-10 text-center tickets-muted text-sm">No tickets match.</div>
        )}
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-500 dark:text-slate-400">
        <span>
          Showing {filtered.length === 0 ? 0 : (safePage - 1) * PAGE_SIZE + 1}–
          {Math.min(safePage * PAGE_SIZE, filtered.length)} of {filtered.length} tickets
          {tickets.filter((t) => !!t.deleted_at === showTrash).length !== filtered.length
            ? ` (filtered from ${tickets.filter((t) => !!t.deleted_at === showTrash).length})`
            : ''}
        </span>
        <div className="flex items-center gap-2">
          <span className="tabular-nums">
            Page {safePage} of {totalTicketPages}
          </span>
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
      </div>

      {showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}

      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-white dark:bg-zinc-900 border border-slate-200 dark:border-white/10 p-5 shadow-xl">
            <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
              {confirmAction.type === 'delete' ? 'Move to trash?' : 'Restore ticket?'}
            </h3>
            <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
              {confirmAction.type === 'delete'
                ? 'This ticket will be moved to trash. You can restore it later.'
                : 'This ticket will be restored to the active list.'}
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                disabled={confirmBusy}
                onClick={() => setConfirmAction(null)}
                className="px-3 py-1.5 text-sm rounded-lg border border-slate-200 dark:border-white/15 text-slate-600 dark:text-slate-300"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={confirmBusy}
                onClick={() => void runConfirm()}
                className={clsx(
                  'px-3 py-1.5 text-sm rounded-lg font-medium text-white',
                  confirmAction.type === 'delete' ? 'bg-rose-600 hover:bg-rose-700' : 'bg-emerald-600 hover:bg-emerald-700',
                )}
              >
                {confirmBusy ? 'Working…' : confirmAction.type === 'delete' ? 'Trash' : 'Restore'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
