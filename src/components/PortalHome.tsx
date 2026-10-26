import { useMemo } from 'react';
import {
  LifeBuoy,
  Ticket,
  MessageSquare,
  Search,
  ClipboardList,
  CheckCircle2,
  ArrowRight,
  Lightbulb,
  Megaphone,
  Sparkles,
} from 'lucide-react';
import { usePlatform } from '../context/PlatformContext';

type Props = {
  displayName: string;
  onNavigate: (view: 'community' | 'help' | 'submit' | 'chat' | 'track' | 'mytickets') => void;
};

const PROCESS = [
  {
    step: '1',
    title: 'Describe the issue',
    body: 'Open Submit request. Include your branch, a clear subject, and what you already tried.',
    icon: ClipboardList,
  },
  {
    step: '2',
    title: 'We route it',
    body: 'Your ticket is assigned using branch and priority so the right queue picks it up.',
    icon: Ticket,
  },
  {
    step: '3',
    title: 'Track progress',
    body: 'Use Track ticket or My tickets anytime to see status linked to your email.',
    icon: Search,
  },
  {
    step: '4',
    title: 'Need it faster?',
    body: 'Urgent account issues → Live chat. Shared tips → Community first.',
    icon: MessageSquare,
  },
];

const TIPS = [
  {
    title: 'Password & account access',
    body: 'Try Account settings first. Many login issues clear after a password reset.',
  },
  {
    title: 'Before you open a ticket',
    body: 'Check Community — other customers often share workarounds for known issues.',
  },
  {
    title: 'Branch context helps',
    body: 'If you do need support, mention your branch so the right team can help faster.',
  },
];

function formatDate(iso?: string) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return '';
  }
}

export default function PortalHome({ displayName, onNavigate }: Props) {
  const { announcements, releases } = usePlatform();
  const first = displayName?.split(' ')[0] || 'there';

  const activeAnnouncements = useMemo(
    () => (announcements || []).filter((a) => a.active !== false).slice(0, 4),
    [announcements],
  );

  const recentReleases = useMemo(
    () =>
      [...(releases || [])]
        .sort((a, b) => (b.released_at || '').localeCompare(a.released_at || ''))
        .slice(0, 4),
    [releases],
  );

  return (
    <div className="w-full max-w-5xl mx-auto space-y-5 pb-2">
      {/* Hero row */}
      <section className="portal-overview-glass rounded-2xl px-5 py-4 sm:px-6 sm:py-5">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-violet-700 dark:text-violet-300/90">
          Customer portal overview
        </p>
        <div className="mt-1 flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
          <div className="min-w-0">
            <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
              Welcome back, {first}
            </h1>
            <p className="mt-1.5 text-sm text-zinc-700 dark:text-zinc-300 leading-relaxed max-w-2xl">
              Self-serve hub for Nexus Ops support — open tickets, chat with agents, track status,
              read guides, or join the customer community from the sidebar.
            </p>
          </div>
          <button
            type="button"
            onClick={() => onNavigate('submit')}
            className="inline-flex shrink-0 items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-semibold hover:bg-brand-700 transition-colors"
          >
            Start a request <ArrowRight size={16} />
          </button>
        </div>
      </section>

      {/* Announcements + Patch notes */}
      <div className="grid lg:grid-cols-2 gap-4">
        <section className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col min-h-[220px]">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-700 dark:text-violet-300 flex items-center justify-center">
              <Megaphone size={16} />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Announcements</h2>
              <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Latest posts from the support team</p>
            </div>
          </div>
          <ul className="flex-1 space-y-2.5">
            {activeAnnouncements.length === 0 && (
              <li className="text-sm text-zinc-600 dark:text-zinc-400 py-6 text-center">
                No active announcements right now.
              </li>
            )}
            {activeAnnouncements.map((a) => (
              <li
                key={a.id || a.title}
                className="rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3.5 py-2.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{a.title}</div>
                  {a.severity && a.severity !== 'info' && (
                    <span
                      className={`text-[10px] font-semibold uppercase tracking-wide px-1.5 py-0.5 rounded ${
                        a.severity === 'critical'
                          ? 'bg-rose-500/20 text-rose-800 dark:text-rose-200'
                          : 'bg-amber-500/20 text-amber-900 dark:text-amber-200'
                      }`}
                    >
                      {a.severity}
                    </span>
                  )}
                </div>
                <p className="text-xs text-zinc-700 dark:text-zinc-300 mt-0.5 leading-relaxed line-clamp-2">
                  {a.body}
                </p>
                {a.created_at && (
                  <div className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-1">{formatDate(a.created_at)}</div>
                )}
              </li>
            ))}
          </ul>
        </section>

        <section className="portal-overview-glass rounded-2xl p-4 sm:p-5 flex flex-col min-h-[220px]">
          <div className="flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-fuchsia-500/15 text-fuchsia-700 dark:text-fuchsia-300 flex items-center justify-center">
              <Sparkles size={16} />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">Patch notes</h2>
              <p className="text-[11px] text-zinc-600 dark:text-zinc-400">Recent product releases</p>
            </div>
          </div>
          <ul className="flex-1 space-y-2.5">
            {recentReleases.length === 0 && (
              <li className="text-sm text-zinc-600 dark:text-zinc-400 py-6 text-center">
                No release notes published yet.
              </li>
            )}
            {recentReleases.map((r) => (
              <li
                key={r.id || r.version}
                className="rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3.5 py-2.5"
              >
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-[10px] font-bold tracking-wide px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-800 dark:text-violet-200">
                    v{r.version}
                  </span>
                  <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{r.title}</div>
                </div>
                <p className="text-xs text-zinc-700 dark:text-zinc-300 mt-0.5 leading-relaxed line-clamp-2">
                  {r.notes}
                </p>
                {r.released_at && (
                  <div className="text-[10px] text-zinc-500 dark:text-zinc-400 mt-1">{formatDate(r.released_at)}</div>
                )}
              </li>
            ))}
          </ul>
        </section>
      </div>

      {/* How support works */}
      <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-700 dark:text-violet-300 flex items-center justify-center">
            <CheckCircle2 size={16} />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">How support works</h2>
            <p className="text-[11px] text-zinc-600 dark:text-zinc-400">From issue to resolution</p>
          </div>
        </div>
        <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-3">
          {PROCESS.map((p) => {
            const Icon = p.icon;
            return (
              <div
                key={p.step}
                className="rounded-xl border border-white/25 dark:border-white/10 bg-white/25 dark:bg-black/20 px-3.5 py-3"
              >
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-violet-600 text-[11px] font-bold text-white">
                    {p.step}
                  </span>
                  <Icon size={14} className="text-violet-600 dark:text-violet-300" />
                </div>
                <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{p.title}</div>
                <p className="text-xs text-zinc-700 dark:text-zinc-300 mt-0.5 leading-relaxed">{p.body}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Channels + tips */}
      <div className="grid lg:grid-cols-2 gap-4">
        <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
          <div className="flex items-center gap-2 mb-3">
            <LifeBuoy size={16} className="text-zinc-500 dark:text-zinc-400" />
            <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">When to use each channel</h2>
          </div>
          <div className="space-y-3 text-xs sm:text-[13px] text-zinc-700 dark:text-zinc-300 leading-relaxed">
            <p>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">Help articles</span>
              {' — '}
              Guides and FAQs without waiting on an agent.
              <button
                type="button"
                onClick={() => onNavigate('help')}
                className="ml-1.5 text-violet-700 dark:text-violet-300 font-medium hover:underline"
              >
                Browse articles
              </button>
            </p>
            <p>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">Contact support</span>
              {' — '}
              Submit request or Live chat for account-specific or urgent issues.
            </p>
            <p>
              <span className="font-semibold text-zinc-900 dark:text-zinc-100">Community</span>
              {' — '}
              Tips and workarounds from other customers — no ticket needed.
              <button
                type="button"
                onClick={() => onNavigate('community')}
                className="ml-1.5 text-violet-700 dark:text-violet-300 font-medium hover:underline"
              >
                Open community
              </button>
            </p>
          </div>
        </section>

        <section className="portal-overview-glass rounded-2xl p-4 sm:p-5">
          <div className="flex items-center gap-2 mb-3">
            <Lightbulb size={16} className="text-amber-500" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-600 dark:text-zinc-400">
              Helpful to know
            </h2>
          </div>
          <ul className="space-y-3">
            {TIPS.map((t) => (
              <li key={t.title} className="flex gap-2.5">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-500" />
                <div>
                  <div className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{t.title}</div>
                  <p className="text-xs text-zinc-700 dark:text-zinc-300 mt-0.5 leading-relaxed">{t.body}</p>
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  );
}
