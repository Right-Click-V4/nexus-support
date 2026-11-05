import clsx from 'clsx';
import { useEffect, useMemo, useState } from 'react';
import { useTickets } from '../context/TicketContext';
import AgentAvatar from './AgentAvatar';
import { getDeskPresence, watchDeskPresence, type DeskAgent } from '../lib/deskPresence';
import { computeOnlineAgents, ONLINE_WINDOW_MS } from '../lib/onlineAgents';

const statusDot: Record<string, string> = {
  online: 'bg-emerald-400',
  busy: 'bg-amber-400',
  away: 'bg-slate-400',
  in_call: 'bg-sky-400',
  custom: 'bg-violet-400',
  offline: 'bg-slate-500',
};

function isDisplayAgent(a: { role?: string; approval_status?: string | null }) {
  const role = (a.role || '').toLowerCase();
  if (role.includes('customer')) return false;
  if (a.approval_status === 'rejected' || a.approval_status === 'pending') return false;
  return true;
}

export default function TeamStatus() {
  const { agents, tickets } = useTickets();
  const [desk, setDesk] = useState<DeskAgent[]>(() => getDeskPresence());
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => watchDeskPresence(setDesk), []);
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), 15_000);
    return () => window.clearInterval(id);
  }, []);

  const team = useMemo(() => {
    const list = agents.filter(isDisplayAgent);
    const seen = new Set<string>();
    return list.filter((a) => {
      const key = (a.email || a.name || a.id).toLowerCase();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }, [agents]);

  const onlineMap = useMemo(() => {
    const rows = computeOnlineAgents(agents, desk, now);
    return new Map(rows.map((r) => [String(r.id), r]));
  }, [agents, desk, now]);

  const activeCount = onlineMap.size;

  return (
    <div className="bg-white dark:bg-zinc-900/90 rounded-2xl border border-violet-100/80 dark:border-white/10 shadow-sm shadow-violet-500/5 p-5">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-slate-800 dark:text-zinc-100">Team Status</h2>
        <span className="text-xs font-medium text-violet-600 dark:text-violet-300 bg-violet-50 dark:bg-violet-500/15 px-2 py-0.5 rounded-full">
          {activeCount} active
        </span>
      </div>
      {team.length === 0 ? (
        <p className="text-xs text-slate-400 py-6 text-center">No agents yet</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {team.map((agent) => {
            const live = onlineMap.get(String(agent.id));
            const presenceStatus = live
              ? (live.status || 'online').toLowerCase()
              : 'offline';
            const count = tickets.filter(
              (t) => t.assignee_id === agent.id && t.status !== 'resolved' && t.status !== 'closed'
            ).length;
            return (
              <div
                key={agent.id}
                className="flex items-center gap-2.5 p-2.5 rounded-xl border border-transparent hover:border-violet-100 dark:hover:border-white/10 hover:bg-violet-50/40 dark:hover:bg-white/5 transition-colors"
              >
                <div className="relative shrink-0">
                  <AgentAvatar agent={agent} size="md" />
                  <div
                    className={clsx(
                      'absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-white dark:border-zinc-900',
                      statusDot[presenceStatus] || statusDot.offline
                    )}
                    title={live ? presenceStatus : 'offline'}
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-medium text-slate-800 dark:text-zinc-100 truncate">{agent.name}</div>
                  <div className="text-[11px] text-slate-500 dark:text-zinc-400 truncate">
                    {count} ticket{count === 1 ? '' : 's'}
                    {agent.is_admin ? ' · Admin' : ''}
                    {' · '}
                    <span className={presenceStatus === 'offline' ? 'text-slate-400' : 'text-emerald-600 dark:text-emerald-400'}>
                      {presenceStatus === 'offline' ? 'Offline' : presenceStatus.charAt(0).toUpperCase() + presenceStatus.slice(1)}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
      <p className="text-[10px] text-slate-400 dark:text-zinc-500 mt-3">
        Active = heartbeat within {Math.round(ONLINE_WINDOW_MS / 1000)}s (desk tab open or recent activity)
      </p>
    </div>
  );
}
