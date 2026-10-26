import {
  BookOpen,
  LifeBuoy,
  Ticket,
  MessageSquare,
  Search,
  Users,
  ClipboardList,
  CheckCircle2,
  ArrowRight,
  Lightbulb,
} from 'lucide-react';

type Props = {
  displayName: string;
  onNavigate: (view: 'community' | 'help' | 'submit' | 'chat' | 'track' | 'mytickets') => void;
};

const PROCESS = [
  {
    step: '1',
    title: 'Describe the issue',
    body: 'Open Submit request from the sidebar. Include your branch, a clear subject, and what you already tried.',
    icon: ClipboardList,
  },
  {
    step: '2',
    title: 'We route it to the right team',
    body: 'Your ticket is assigned using the branch and priority you set so the correct support queue picks it up.',
    icon: Ticket,
  },
  {
    step: '3',
    title: 'Track progress anytime',
    body: 'Use Track ticket with your ticket ID, or open My tickets to see everything linked to your email.',
    icon: Search,
  },
  {
    step: '4',
    title: 'Need a faster path?',
    body: 'For urgent account issues, start Live chat. For shared tips, use Community before opening a ticket.',
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

export default function PortalHome({ displayName, onNavigate }: Props) {
  const first = displayName?.split(' ')[0] || 'there';

  return (
    <div className="max-w-3xl mx-auto space-y-8 pb-2">
      {/* Intro */}
      <section className="space-y-2">
        <p className="text-[11px] font-semibold uppercase tracking-wider text-violet-600/80 dark:text-violet-300/90">
          Customer portal overview
        </p>
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-zinc-900 dark:text-zinc-50">
          Welcome back, {first}
        </h1>
        <p className="text-sm sm:text-[15px] text-zinc-600 dark:text-zinc-300 leading-relaxed max-w-2xl">
          This portal is your self-serve hub for Nexus Ops support. Use the sidebar to open a ticket,
          chat with an agent, track status, read guides, or join the customer community — without
          waiting for someone to email you first.
        </p>
      </section>

      {/* How to submit / process */}
      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-violet-500/15 text-violet-600 dark:text-violet-300 flex items-center justify-center">
            <CheckCircle2 size={16} />
          </div>
          <div>
            <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">How support works</h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400">A simple path from issue to resolution</p>
          </div>
        </div>

        <ol className="relative space-y-0 border-l border-violet-300/40 dark:border-violet-500/30 ml-3.5 pl-5">
          {PROCESS.map((p) => {
            const Icon = p.icon;
            return (
              <li key={p.step} className="relative pb-6 last:pb-0">
                <span className="absolute -left-[1.55rem] top-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-violet-600 text-[11px] font-bold text-white shadow-sm shadow-violet-900/30">
                  {p.step}
                </span>
                <div className="flex items-start gap-2.5">
                  <Icon size={16} className="mt-0.5 shrink-0 text-violet-500 dark:text-violet-300" />
                  <div>
                    <div className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{p.title}</div>
                    <p className="text-xs sm:text-[13px] text-zinc-500 dark:text-zinc-400 mt-0.5 leading-relaxed">
                      {p.body}
                    </p>
                  </div>
                </div>
              </li>
            );
          })}
        </ol>

        <button
          type="button"
          onClick={() => onNavigate('submit')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-semibold hover:bg-brand-700 transition-colors"
        >
          Start a request <ArrowRight size={16} />
        </button>
      </section>

      {/* When to use what — plain text, not action cards */}
      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <LifeBuoy size={16} className="text-zinc-400" />
          <h2 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">When to use each channel</h2>
        </div>
        <div className="text-xs sm:text-[13px] text-zinc-600 dark:text-zinc-300 leading-relaxed space-y-2.5 border-t border-zinc-200/60 dark:border-white/10 pt-3">
          <p>
            <span className="font-semibold text-zinc-800 dark:text-zinc-100">Help articles</span>
            {' — '}
            Guides and FAQs you can use without waiting on an agent.
            <button
              type="button"
              onClick={() => onNavigate('help')}
              className="ml-1.5 text-violet-600 dark:text-violet-300 font-medium hover:underline"
            >
              Browse articles
            </button>
          </p>
          <p>
            <span className="font-semibold text-zinc-800 dark:text-zinc-100">When to contact support</span>
            {' — '}
            Use Submit request or Live chat for account-specific or urgent issues. Prefer Community for
            tips and workarounds that other customers already solved.
          </p>
          <p>
            <span className="font-semibold text-zinc-800 dark:text-zinc-100">Community</span>
            {' — '}
            Chat with other customers about issues, workarounds, and tips — without creating a ticket.
            <button
              type="button"
              onClick={() => onNavigate('community')}
              className="ml-1.5 text-violet-600 dark:text-violet-300 font-medium hover:underline"
            >
              Open community
            </button>
          </p>
        </div>
      </section>

      {/* Helpful to know — list, not heavy cards */}
      <section className="space-y-3">
        <div className="flex items-center gap-2">
          <Lightbulb size={16} className="text-amber-500" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-500 dark:text-zinc-400">
            Helpful to know
          </h2>
        </div>
        <ul className="space-y-3 border-t border-zinc-200/60 dark:border-white/10 pt-3">
          {TIPS.map((t) => (
            <li key={t.title} className="flex gap-3">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-violet-400" />
              <div>
                <div className="text-sm font-medium text-zinc-800 dark:text-zinc-100">{t.title}</div>
                <p className="text-xs sm:text-[13px] text-zinc-500 dark:text-zinc-400 mt-0.5 leading-relaxed">
                  {t.body}
                </p>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
