/* analytics-dark-v1 */
import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { useTickets } from '../context/TicketContext';
import { Ticket, Layers, CheckCircle2, TrendingUp } from 'lucide-react';

const PRIORITY_COLORS = ['#f97316', '#8b5cf6', '#93c5fd'];
const CHANNEL_COLORS = ['#8b5cf6', '#0ea5e9', '#d946ef', '#f59e0b', '#64748b'];

export default function AnalyticsPage() {
  const { tickets } = useTickets();
  const live = useMemo(() => tickets.filter((t) => !t.deleted_at), [tickets]);

  const byStatus = useMemo(() => {
    const map: Record<string, number> = {};
    for (const t of live) {
      const key = t.status === 'new' ? 'new' : t.status;
      map[key] = (map[key] || 0) + 1;
    }
    return Object.entries(map).map(([name, value]) => ({ name, value }));
  }, [live]);

  const byPriority = useMemo(() => {
    const order = ['high', 'medium', 'low', 'critical'];
    const map: Record<string, number> = {};
    for (const t of live) {
      map[t.priority] = (map[t.priority] || 0) + 1;
    }
    return order
      .filter((k) => map[k])
      .map((name) => ({ name, value: map[name] }));
  }, [live]);

  const byChannel = useMemo(() => {
    const map: Record<string, number> = {};
    for (const t of live) {
      const ch = (t.channel || 'other').toLowerCase();
      map[ch] = (map[ch] || 0) + 1;
    }
    return Object.entries(map).map(([name, value]) => ({ name, value }));
  }, [live]);

  const open = live.filter((t) => t.status === 'open' || t.status === 'new').length;
  const resolved = live.filter((t) => t.status === 'resolved' || t.status === 'closed').length;
  const rate = live.length ? Math.round((resolved / live.length) * 100) : 0;

  const metrics = [
    { label: 'Total tickets', value: live.length, tint: 'from-violet-500/15 to-fuchsia-500/10', icon: Ticket, iconColor: 'text-violet-600 dark:text-violet-300' },
    { label: 'Open', value: open, tint: 'from-amber-500/15 to-orange-500/10', icon: Layers, iconColor: 'text-amber-600 dark:text-amber-300' },
    { label: 'Resolved', value: resolved, tint: 'from-emerald-500/15 to-teal-500/10', icon: CheckCircle2, iconColor: 'text-emerald-600 dark:text-emerald-300' },
    { label: 'Resolution rate', value: `${rate}%`, tint: 'from-sky-500/15 to-indigo-500/10', icon: TrendingUp, iconColor: 'text-sky-600 dark:text-sky-300' },
  ];

  if (live.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-sm text-slate-400">
        No ticket data yet.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Analytics</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Ticket volume, priority mix, and channels</p>
      </div>

      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {metrics.map((m) => {
          const Icon = m.icon;
          return (
            <div
              key={m.label}
              className={`relative overflow-hidden rounded-2xl border border-violet-100/70 dark:border-white/10 bg-gradient-to-br ${m.tint} p-5 shadow-sm`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">{m.label}</div>
                  <div className="text-2xl font-bold text-slate-900 dark:text-slate-100 mt-1.5 tabular-nums">{m.value}</div>
                </div>
                <div className={`w-10 h-10 rounded-xl bg-white/80 dark:bg-white/10 border border-white dark:border-white/15 flex items-center justify-center ${m.iconColor}`}>
                  <Icon size={18} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid lg:grid-cols-2 gap-5">
        <div className="bg-white dark:bg-white/[0.04] rounded-2xl border border-violet-100/80 dark:border-white/10 shadow-sm p-5">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">By status</h3>
            <span className="text-[11px] text-slate-400">{live.length} tickets</span>
          </div>
          <div className="h-64 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byStatus}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-white/[0.04] rounded-2xl border border-violet-100/80 dark:border-white/10 shadow-sm p-5">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">By priority</h3>
          </div>
          <div className="h-64 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={byPriority} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={3}>
                  {byPriority.map((_, i) => (
                    <Cell key={i} fill={PRIORITY_COLORS[i % PRIORITY_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend
                  formatter={(value) => <span className="text-xs text-slate-600 dark:text-slate-300 capitalize">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white dark:bg-white/[0.04] rounded-2xl border border-violet-100/80 dark:border-white/10 shadow-sm p-5 lg:col-span-2">
          <div className="flex items-center justify-between mb-1">
            <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">By channel</h3>
          </div>
          <div className="h-64 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byChannel}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.25)" />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip />
                <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                  {byChannel.map((_, i) => (
                    <Cell key={i} fill={CHANNEL_COLORS[i % CHANNEL_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
