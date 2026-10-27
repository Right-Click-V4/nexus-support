/* tickets-table-v2 */
import { useEffect, useMemo, useState } from 'react';
import { Plus, Search, Download, Trash2, RotateCcw } from 'lucide-react';
import clsx from 'clsx';
import { useTickets } from '../context/TicketContext';
import type { Priority, Status } from '../types';
import { formatSlaCountdown } from '../lib/slaFormat';
import CreateTicketModal from './CreateTicketModal';
import TicketDetail from './TicketDetail';

const priorityStyles: Record<string, string> = {
  critical: 'bg-rose-100 text-rose-700',
  high: 'bg-orange-100 text-orange-700',
  medium: 'bg-brand-100 text-brand-700',
  low: 'bg-slate-100 text-slate-600',
};

const statusStyles: Record<string, string> = {
  new: 'bg-brand-50 text-brand-700 border-brand-200',
  open: 'bg-amber-50 text-amber-700 border-amber-200',
  pending: 'bg-violet-50 text-violet-700 border-violet-200',
  resolved: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  'on-hold': 'bg-slate-50 text-slate-600 border-slate-200',
};

export default function TicketsPage() {
  const { tickets, loading, updateTicket, softDeleteTicket } = useTickets();
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<Status | 'all'>('all');
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');
  const [channelFilter, setChannelFilter] = useState<'all' | 'portal' | 'email' | 'chat' | 'phone'>('all');
  const [slaFilter, setSlaFilter] = useState<'all' | 'breach' | 'warn'>('all');
  const [showTrash, setShowTrash] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [, setTick] = useState(0);

  useEffect(() => {
    const id = window.setInterval(() => setTick((n) => n + 1), 30_000);
    return () => clearInterval(id);
  }, []);

  const filtered = useMemo(() => {
    return tickets.filter((t) => {
      const isDeleted = !!t.deleted_at;
      if (showTrash ? !isDeleted : isDeleted) return false;
      if (statusFilter !== 'all' && t.status !== statusFilter) return false;
      if (priorityFilter !== 'all' && t.priority !== priorityFilter) return false;
      if (channelFilter !== 'all' && t.channel !== channelFilter) return false;
      if (slaFilter !== 'all') {
        const sla = formatSlaCountdown(t.sla_due_at, t.status);
        if (slaFilter === 'breach' && sla.tone !== 'breach') return false;
        if (slaFilter === 'warn' && sla.tone !== 'warn' && sla.tone !== 'breach') return false;
      }
      if (search) {
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
  }, [tickets, search, statusFilter, priorityFilter, channelFilter, slaFilter, showTrash]);

  const selected = selectedId ? tickets.find((t) => t.id === selectedId) : null;
  const breachCount = tickets.filter(
    (t) => !t.deleted_at && t.status !== 'resolved' && formatSlaCountdown(t.sla_due_at, t.status).tone === 'breach'
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

  const softDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Move this ticket to trash?')) return;
    await softDeleteTicket(id);
  };

  const restore = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await updateTicket(id, { deleted_at: null });
  };

  return (
    <div className="space-y-4">
      {breachCount > 0 && (
        <button
          type="button"
          onClick={() => setSlaFilter('breach')}
          className="w-full text-left rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900"
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
            className="w-full pl-9 pr-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500/30"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as Status | 'all')}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
        >
          <option value="all">All statuses</option>
          <option value="new">New</option>
          <option value="open">Open</option>
          <option value="pending">Pending</option>
          <option value="on-hold">On hold</option>
          <option value="resolved">Resolved</option>
        </select>
        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value as Priority | 'all')}
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
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
          className="text-sm px-3 py-2 border border-slate-200 rounded-lg bg-white"
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
          className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white"
        >
          <option value="all">All SLA</option>
          <option value="warn">At risk</option>
          <option value="breach">Breached</option>
        </select>
        <button
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
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-10 text-center text-slate-400 text-sm">Loading tickets...</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr className="text-left text-slate-500">
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Subject</th>
                <th className="px-4 py-3 font-medium">Customer</th>
                <th className="px-4 py-3 font-medium">Branch</th>
                <th className="px-4 py-3 font-medium">Priority</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Channel</th>
                <th className="px-4 py-3 font-medium">Submitted</th>
                <th className="px-4 py-3 font-medium">SLA</th>
                <th className="px-4 py-3 font-medium">Assignee</th>
                <th className="px-4 py-3 font-medium w-20"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((t) => {
                const sla = formatSlaCountdown(t.sla_due_at, t.status);
                return (
                  <tr
                    key={t.id}
                    onClick={() => setSelectedId(t.id)}
                    className={clsx(
                      'border-b border-slate-100 hover:bg-brand-50/50 cursor-pointer transition-colors',
                      t.status === 'new' && t.channel === 'portal' && 'bg-violet-50/80 ring-1 ring-inset ring-violet-200/60',
                      t.status === 'new' && t.channel !== 'portal' && 'bg-brand-50/40'
                    )}
                  >
                    <td className="px-4 py-3 font-mono text-xs text-slate-500">{t.id}</td>
                    <td className="px-4 py-3 font-medium text-slate-800 max-w-[240px]">
                      <div className="truncate" title={t.title}>{t.title}</div>
                      {t.description ? (
                        <div className="text-[11px] text-slate-400 truncate mt-0.5 font-normal" title={t.description}>
                          {t.description}
                        </div>
                      ) : null}
                      {(t.tags || []).length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {(t.tags || []).slice(0, 3).map((tag) => (
                            <span key={tag} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-normal">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-slate-800 font-medium">{t.customer_name}</div>
                      {t.customer_email && (
                        <div className="text-[11px] text-slate-400 truncate max-w-[140px]">{t.customer_email}</div>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-600 text-xs max-w-[120px] truncate" title={t.branch || ''}>
                      {t.branch || '—'}
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-[10px] font-bold uppercase px-1.5 py-0.5 rounded', priorityStyles[t.priority])}>
                        {t.priority}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={clsx('text-xs font-medium px-2 py-0.5 rounded border capitalize', statusStyles[t.status])}>
                        {t.status.replace('-', ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'text-xs font-semibold tabular-nums px-2 py-0.5 rounded',
                          sla.tone === 'breach' && 'bg-rose-100 text-rose-700',
                          sla.tone === 'warn' && 'bg-amber-100 text-amber-800',
                          sla.tone === 'ok' && 'bg-emerald-50 text-emerald-700',
                          sla.tone === 'done' && 'text-slate-400'
                        )}
                        title={t.sla_due_at ? new Date(t.sla_due_at).toLocaleString() : 'No SLA'}
                      >
                        {sla.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span
                        className={clsx(
                          'text-[10px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded',
                          t.channel === 'portal' && 'bg-violet-100 text-violet-700',
                          t.channel === 'email' && 'bg-sky-100 text-sky-700',
                          t.channel === 'chat' && 'bg-fuchsia-100 text-fuchsia-700',
                          t.channel === 'phone' && 'bg-amber-100 text-amber-800',
                          !['portal', 'email', 'chat', 'phone'].includes(t.channel) && 'bg-slate-100 text-slate-600'
                        )}
                      >
                        {t.channel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-[11px] text-slate-500 whitespace-nowrap tabular-nums" title={new Date(t.created_at).toLocaleString()}>
                      {new Date(t.created_at).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-4 py-3 text-slate-600">{t.assignee?.initials || t.assignee?.name || '—'}</td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {showTrash ? (
                        <button type="button" onClick={(e) => void restore(t.id, e)} className="p-1.5 text-slate-400 hover:text-emerald-600" title="Restore">
                          <RotateCcw size={14} />
                        </button>
                      ) : (
                        <button type="button" onClick={(e) => void softDelete(t.id, e)} className="p-1.5 text-slate-400 hover:text-rose-600" title="Trash">
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
          <div className="p-10 text-center text-slate-400 text-sm">No tickets match.</div>
        )}
      </div>

      <div className="text-xs text-slate-500">
        Showing {filtered.length} of {tickets.filter((t) => !!t.deleted_at === showTrash).length} tickets
      </div>

      {showCreate && <CreateTicketModal onClose={() => setShowCreate(false)} />}
      {selected && <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />}
    </div>
  );
}
