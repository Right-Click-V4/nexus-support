import { useMemo, useState } from 'react';
import clsx from 'clsx';
import { useTickets } from '../context/TicketContext';
import TicketDetail from './TicketDetail';

const priorityStyles: Record<string, string> = {
  critical: 'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300',
  high: 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-300',
  medium: 'bg-brand-100 text-brand-700 dark:bg-violet-500/20 dark:text-violet-300',
  low: 'bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-zinc-300',
};

const statusStyles: Record<string, string> = {
  new: 'text-brand-600 dark:text-violet-300',
  open: 'text-amber-600 dark:text-amber-400',
  pending: 'text-violet-600 dark:text-violet-300',
  resolved: 'text-emerald-600 dark:text-emerald-400',
  'on-hold': 'text-slate-500 dark:text-zinc-400',
};

function isOpenStatus(status: string) {
  const s = (status || '').toLowerCase();
  return s !== 'resolved' && s !== 'closed';
}

export default function MyQueue() {
  const { tickets, currentAgent } = useTickets();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const myTickets = useMemo(() => {
    if (!currentAgent?.id) return [];
    const agentId = String(currentAgent.id);
    const agentName = (currentAgent.name || '').trim().toLowerCase();
    return tickets
      .filter((t) => {
        if (!isOpenStatus(t.status)) return false;
        if (t.assignee_id && String(t.assignee_id) === agentId) return true;
        if (t.assignee?.id && String(t.assignee.id) === agentId) return true;
        if (!t.assignee_id && agentName && (t.assignee?.name || '').trim().toLowerCase() === agentName) {
          return true;
        }
        return false;
      })
      .sort((a, b) => {
        const pa = { critical: 0, high: 1, medium: 2, low: 3 }[a.priority] ?? 4;
        const pb = { critical: 0, high: 1, medium: 2, low: 3 }[b.priority] ?? 4;
        if (pa !== pb) return pa - pb;
        return new Date(b.updated_at || b.created_at || 0).getTime() - new Date(a.updated_at || a.created_at || 0).getTime();
      });
  }, [tickets, currentAgent]);

  const shown = myTickets.slice(0, 10);
  const selected = selectedId ? tickets.find((t) => t.id === selectedId) : null;

  return (
    <div className="bg-white dark:bg-zinc-900/90 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-800 dark:text-zinc-100 flex items-center gap-2">
          My Queue
          <span className="bg-brand-100 dark:bg-violet-500/20 text-brand-700 dark:text-violet-300 text-xs font-bold px-1.5 py-0.5 rounded-full">
            {myTickets.length}
          </span>
        </h2>
        {currentAgent && (
          <span className="text-[10px] text-slate-400 dark:text-zinc-500 truncate max-w-[10rem]">
            {currentAgent.name}
          </span>
        )}
      </div>

      <div className="space-y-2">
        {!currentAgent && (
          <p className="text-sm text-slate-500 dark:text-zinc-400 py-4 text-center">Sign in as an agent to see your queue</p>
        )}
        {currentAgent && myTickets.length === 0 && (
          <p className="text-sm text-slate-500 dark:text-zinc-400 py-4 text-center">
            No tickets assigned to you
          </p>
        )}
        {shown.map((ticket) => (
          <div
            key={ticket.id}
            onClick={() => setSelectedId(ticket.id)}
            className="flex items-start gap-3 p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-white/5 transition-colors cursor-pointer border border-transparent hover:border-slate-100 dark:hover:border-white/10"
          >
            <div
              className={clsx(
                'text-[10px] font-bold uppercase px-1.5 py-0.5 rounded mt-0.5 shrink-0',
                priorityStyles[ticket.priority] || priorityStyles.low
              )}
            >
              {ticket.priority}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-xs text-slate-400 dark:text-zinc-500 font-mono shrink-0">
                  {String(ticket.id).slice(0, 8)}
                </span>
                <span className={clsx('text-xs font-semibold capitalize shrink-0', statusStyles[ticket.status] || 'text-slate-500')}>
                  {ticket.status}
                </span>
              </div>
              <div className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate mt-0.5">
                {ticket.title}
              </div>
              {(ticket.customer_name || ticket.branch) && (
                <div className="text-[11px] text-slate-400 dark:text-zinc-500 truncate">
                  {[ticket.customer_name, ticket.branch].filter(Boolean).join(' · ')}
                </div>
              )}
            </div>
          </div>
        ))}
        {myTickets.length > shown.length && (
          <p className="text-[11px] text-center text-slate-400 dark:text-zinc-500 pt-1">
            +{myTickets.length - shown.length} more assigned
          </p>
        )}
      </div>

      {selected && (
        <TicketDetail ticket={selected} onClose={() => setSelectedId(null)} />
      )}
    </div>
  );
}
