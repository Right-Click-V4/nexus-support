/* tickets-claim-v1 */
/* sla-resolved-not-closed-v1 */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Plus, Search, Trash2, RotateCcw } from 'lucide-react';
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
  open: 'bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:border-amber-400/30',
  pending: 'bg-violet-50 text-violet-800 border-violet-200 dark:bg-violet-500/15 dark:text-violet-300 dark:border-violet-400/30',
  resolved: 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-500/15 dark:text-emerald-300 dark:border-emerald-400/30',
  'on-hold': 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-white/8 dark:text-slate-300 dark:border-white/15',
  closed: 'bg-rose-50 text-rose-800 border-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:border-rose-400/30',
};

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
  const { tickets, loading, updateTicket, softDeleteTicket, currentAgent } = useTickets();
  const claimTicket = async (id: string, e?: { stopPropagation: () => void }) => {
    e?.stopPropagation();
    if (!currentAgent?.id) return;
    await updateTicket(id, { assignee_id: currentAgent.id, status: 'open' as Status }, { silent: true });
  };
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
    breached.forEach((t) => closedBreachRef.current.add(t.id));
    void Promise.all(
      breached.map(async (t) => {
        try {
          const tags = Array.from(new Set([...(t.tags || []), 'sla-auto-closed']));
          await updateTicket(t.id, { status: 'resolved' as Status, tags }, { silent: true });
        } catch {
          /* already marked */
        }
      }),
    );
  }, [tickets, updateTicket]);

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      if (showTrash ? !t.deleted_at : t.deleted_at) return false;
      if (statusFilter !== 'all' && t.status !== statusFilter) return false;
      if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;
      if (channelFilter !== 'all' && String(t.channel || '').toLowerCase() !== channelFilter) return false;
      if (slaFilter !== 'all') {
        const tone = formatSlaCountdown(t.sla_due_at, t.status).tone;
        if (slaFilter === 'breach' && tone !== 'breach') return false;
        if (slaFilter === 'warn' && tone !== 'warn') return false;
      }
      if (dateFilter) {
        const d = new Date(t.created_at).toISOString().slice(0, 10);
        if (d !== dateFilter) return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        const hay = `${t.id} ${t.title} ${t.customer_name} ${t.customer_email || ''} ${t.branch || ''}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [tickets, showTrash, statusFilter, priorityFilter, channelFilter, slaFilter, dateFilter, search]);

  const pageSize = 30;
  const pages = Math.max(1, Math.ceil(filtered.length / pageSize));
  const page = Math.min(ticketPage, pages);
  const pageRows = filtered.slice((page - 1) * pageSize, page * pageSize);
  const selected = selectedId ? tickets.find((x) => x.id === selectedId) : null;

  const softDelete = async (id: string, e: { stopPropagation: () => void }) => {
    e.stopPropagation();
    setConfirmAction({ type: 'delete', id });
  };
  const restore = async (id: string, e: { stopPropagation: () => void }) => {
    e.stopPropagation();
    setConfirmAction({ type: 'restore', id });
  };

  const runConfirm = async () => {
    if (!confirmAction) return;
    setConfirmBusy(true);
    try {
      if (confirmAction.type === 'delete') await softDeleteTicket(confirmAction.id);
      else await updateTicket(confirmAction.id, { deleted_at: null as unknown as string }, { silent: true });
    } finally {
      setConfirmBusy(false);
      setConfirmAction(null);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-[12rem]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            value={search}
            onChange={(e) => { setSearch(e.target.value); setTicketPage(1); }}
            placeholder="Search tickets…"
            className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-slate-200 dark:border-white/10 bg-white dark:bg-zinc-900"
          />
        </div>
        <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value as Status | 'all'); setTicketPage(1); }} className="text-sm rounded-lg border border-slate-200 dark:border-white/10 px-2 py-2 bg-white dark:bg-zinc-900">
          <option value="all">All status</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="on-hold">On hold</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <select value={priorityFilter} onChange={(e) => { setPriorityFilter(e.target.value as Priority | 'all'); setTicketPage(1); }} className="text-sm rounded-lg border border-slate-200 dark:border-white/10 px-2 py-2 bg-white dark:bg-zinc-900">
          <option value="all">All priority</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <button type="button" onClick={() => setShowTrash((v) => !v)} className={clsx('text-sm px-3 py-2 rounded-lg border', showTrash ? 'border-rose-400 text-rose-600' : 'border-slate-200 dark:border-white/10')}>
          {showTrash ? 'Active tickets' : 'Trash'}
        </button>
        <button type="button" onClick={() => setShowCreate(true)} className="inline-flex items-center gap-1 text-sm font-medium text-white bg-violet-600 hover:bg-violet-500 px-3 py-2 rounded-lg">
          <Plus size={16} /> New ticket
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-white/10 overflow-hidden bg-white dark:bg-zinc-900/80">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-[11px] uppercase tracking-wide text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-white/10">
              <tr>
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
              {loading && pageRows.length === 0 && (
                <tr><td colSpan={11} className="px-4 py-8 text-center text-slate-400">Loading…</td></tr>
              )}
              {!loading && pageRows.length === 0 && (
                <tr><td colSpan={11} className="px-4 py-8 text-center text-slate-400">No tickets</td></tr>
              )}
              {pageRows.map((t) => {
                const sla = formatSlaCountdown(t.sla_due_at, t.status);
                return (
                  <tr
                    key={t.id}
                    onClick={() => setSelectedId(t.id)}
                    className={clsx(
                      'border-t border-slate-100 dark:border-white/5 cursor-pointer hover:bg-violet-50/40 dark:hover:bg-white/5',
                      t.status === 'closed' && 'bg-rose-50/40 dark:bg-rose-500/5',
                    )}
                  >
                    <td className="px-4 py-3 font-mono text-[11px] text-slate-500">{t.id}</td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-900 dark:text-zinc-100 truncate max-w-[14rem]">{t.title}</div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-sm truncate">{t.customer_name}</div>
                      <div className="text-[11px] text-slate-400 truncate">{t.customer_email}</div>
                    </td>
                    <td className="px-4 py-3 text-xs">{t.branch || '—'}</td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-[10px] font-bold uppercase px-2 py-0.5 rounded-md', priorityStyles[t.priority] || priorityStyles.low)}>{t.priority}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-[10px] font-semibold capitalize px-2 py-0.5 rounded-md border', statusStyles[t.status] || statusStyles.open)}>{t.status}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-[10px] font-semibold px-2 py-0.5 rounded-md', sla.tone === 'breach' && 'bg-rose-100 text-rose-800 dark:bg-rose-500/20 dark:text-rose-300', sla.tone === 'warn' && 'bg-amber-100 text-amber-900 dark:bg-amber-500/20 dark:text-amber-300', sla.tone === 'ok' && 'bg-emerald-50 text-emerald-800 dark:bg-emerald-500/15 dark:text-emerald-300')}>{sla.label}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-[10px] font-semibold uppercase px-2 py-0.5 rounded-md', channelStyles[String(t.channel || '').toLowerCase()] || channelFallback)}>{t.channel || '—'}</span>
                    </td>
                    <td className="px-4 py-3 text-[11px] text-slate-400 whitespace-nowrap">
                      {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {t.assignee_id ? (
                        <span className="text-sm">
                          {(t.assignee?.name ? t.assignee.name.trim().split(/\s+/)[0] : null) || t.assignee?.initials || '—'}
                        </span>
                      ) : currentAgent && t.status !== 'resolved' && t.status !== 'closed' && !t.deleted_at ? (
                        <button
                          type="button"
                          onClick={(e) => void claimTicket(t.id, e)}
                          className="text-[11px] font-semibold px-2.5 py-1 rounded-md bg-violet-600 text-white hover:bg-violet-500 shadow-sm"
                          title="Assign this ticket to me"
                        >
                          Claim
                        </button>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {showTrash ? (
                        <button type="button" onClick={(e) => void restore(t.id, e)} className="p-1.5 text-slate-400 hover:text-emerald-600" title="Restore"><RotateCcw size={14} /></button>
                      ) : (
                        <button type="button" onClick={(e) => void softDelete(t.id, e)} className="p-1.5 text-slate-400 hover:text-rose-600" title="Trash"><Trash2 size={14} /></button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {pages > 1 && (
          <div className="flex items-center justify-between px-4 py-2 border-t border-slate-100 dark:border-white/10 text-xs">
            <span className="text-slate-400">{filtered.length} tickets</span>
            <div className="flex gap-2">
              <button type="button" disabled={page <= 1} onClick={() => setTicketPage((p) => p - 1)} className="px-2 py-1 rounded border border-slate-200 dark:border-white/10 disabled:opacity-40">Prev</button>
              <span>{page} / {pages}</span>
              <button type="button" disabled={page >= pages} onClick={() => setTicketPage((p) => p + 1)} className="px-2 py-1 rounded border border-slate-200 dark:border-white/10 disabled:opacity-40">Next</button>
            </div>
          </div>
        )}
      </div>

      {showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}
      {selected && <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />}
      {confirmAction && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white dark:bg-zinc-900 rounded-xl p-5 max-w-sm w-full shadow-xl">
            <p className="text-sm mb-4">{confirmAction.type === 'delete' ? 'Move this ticket to trash?' : 'Restore this ticket?'}</p>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setConfirmAction(null)} className="px-3 py-1.5 text-sm rounded-lg border border-slate-200 dark:border-white/10">Cancel</button>
              <button type="button" disabled={confirmBusy} onClick={() => void runConfirm()} className="px-3 py-1.5 text-sm rounded-lg bg-violet-600 text-white">{confirmBusy ? '…' : 'Confirm'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
