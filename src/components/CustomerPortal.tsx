import { useState, useMemo, useEffect } from 'react';
import {
  Search, CheckCircle2, Ticket, BookOpen, ArrowLeft, MessageSquare,
  LogOut, User, Star, Home, ExternalLink, Users,
} from 'lucide-react';
import { useTickets } from '../context/TicketContext';
import { useAuth } from '../context/AuthContext';
import { usePlatform } from '../context/PlatformContext';
import type { Priority, Ticket as TicketType } from '../types';
import { INITIAL_BRANCHES } from '../data';
import PortalLiveChat from './PortalLiveChat';
import PortalAuthGate from './PortalAuthGate';
import PortalHome from './PortalHome';
import PortalAnnouncementMarquee from './PortalAnnouncementMarquee';
import PortalCommunityChat from './PortalCommunityChat';
import ThemeToggle from './ThemeToggle';
import PortalSpaceLoungeBg from './PortalSpaceLoungeBg';

interface Props { onBackToAgent?: () => void; }
type PortalView = 'home' | 'submit' | 'track' | 'success' | 'help' | 'chat' | 'account' | 'mytickets' | 'community';

const HELP_ARTICLES = [
  { title: 'Reset your password', body: 'Go to Account → Sign in. Use the same email you registered with.' },
  { title: 'Check service status', body: 'Visit status.nexus.support for live incident updates before opening a ticket.' },
  { title: 'Billing & invoices', body: 'Invoices are emailed on the 1st of each month. Include your invoice number when submitting a request.' },
  { title: 'API rate limits', body: 'Free plans allow 60 requests/minute. Pro plans allow 600.' },
];

const BRANCH_OPTIONS = INITIAL_BRANCHES.map((b) => b.name);

const VIEW_META: Record<PortalView, { title: string; desc: string; iconColor: string }> = {
  home: { title: 'Overview', desc: 'How this portal works and how to get support.', iconColor: 'text-violet-700 dark:text-violet-300' },
  submit: { title: 'Submit a request', desc: 'Open a support ticket with your branch and details.', iconColor: 'text-amber-600 dark:text-amber-400' },
  track: { title: 'Track a ticket', desc: 'Look up status updates by ticket ID and email.', iconColor: 'text-emerald-600 dark:text-emerald-400' },
  success: { title: 'Request received', desc: 'Your ticket was created successfully.', iconColor: 'text-violet-700 dark:text-violet-300' },
  help: { title: 'Help articles', desc: 'Guides and FAQs you can use without waiting on an agent.', iconColor: 'text-indigo-700 dark:text-indigo-300' },
  chat: { title: 'Live chat', desc: 'Talk to a support agent in real time.', iconColor: 'text-fuchsia-600 dark:text-fuchsia-400' },
  account: { title: 'Account', desc: 'Profile details and sign-in information.', iconColor: 'text-pink-600 dark:text-pink-400' },
  mytickets: { title: 'My tickets', desc: 'Review tickets you have opened with support.', iconColor: 'text-blue-600 dark:text-blue-400' },
  community: { title: 'Community', desc: 'Chat with other customers about tips and workarounds.', iconColor: 'text-sky-600 dark:text-sky-400' },
};

function BrandMark({ className = 'w-8 h-8' }: { className?: string }) {
  return (
    <div className={`${className} rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-md shadow-brand-900/40`}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <circle cx="12" cy="12" r="3" fill="white" />
        <path d="M12 3a9 9 0 0 1 9 9" stroke="white" strokeWidth="2.2" strokeLinecap="round" opacity="0.95" />
        <path d="M12 21a9 9 0 0 1-9-9" stroke="white" strokeWidth="2.2" strokeLinecap="round" opacity="0.55" />
      </svg>
    </div>
  );
}

/* footer-flow-v2 */ /* community-glass-v1 */ /* chrome-footer-v2 */ /* nav-signout-v1 */
export default function CustomerPortal({ onBackToAgent }: Props) {
  const { createTicket, findTicket, tickets, ticketsForEmail } = useTickets();
  const { user, accountRole, signOut, requiresAuth } = useAuth();
  const { addSurvey, surveys } = usePlatform();
  const [view, setView] = useState<PortalView>('home');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [branch, setBranch] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority>('medium');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [created, setCreated] = useState<TicketType | null>(null);
  const [trackId, setTrackId] = useState('');
  const [trackEmail, setTrackEmail] = useState('');
  const [tracked, setTracked] = useState<TicketType | null>(null);
  const [trackError, setTrackError] = useState('');
  const [csatScore, setCsatScore] = useState(5);
  const [csatComment, setCsatComment] = useState('');
  const [csatDone, setCsatDone] = useState(false);
  const [csatSaving, setCsatSaving] = useState(false);

  const isCustomerSession = !!user && accountRole === 'customer';
  const myTickets = isCustomerSession && user?.email ? ticketsForEmail(user.email) : [];
  const displayName =
    (user?.user_metadata?.full_name as string) || user?.email?.split('@')[0] || 'Customer';
  const initials = displayName.slice(0, 2).toUpperCase();

  useEffect(() => {
    if (!isCustomerSession || !user) return;
    const display = (user.user_metadata?.full_name as string) || '';
    if (display) setName((n) => n || display);
    if (user.email) setEmail((e) => e || user.email || '');
  }, [isCustomerSession, user]);


  // Hard-reload this portal tab when Admin publishes/deletes an announcement
  useEffect(() => {
    let lastTick = '';
    try { lastTick = localStorage.getItem('nexus-announce-tick') || ''; } catch { /* ignore */ }

    const hardReload = () => {
      try {
        const url = window.location.href;
        window.location.replace(url);
      } catch {
        try { window.location.reload(); } catch { /* ignore */ }
      }
    };

    const onStorage = (e: StorageEvent) => {
      if (e.key === 'nexus-announce-tick' || e.key === 'nexus-announce' || e.key === 'nexus-announce-channels') {
        hardReload();
      }
    };
    window.addEventListener('storage', onStorage);

    let bc: BroadcastChannel | null = null;
    try {
      bc = new BroadcastChannel('nexus-announce');
      bc.onmessage = () => hardReload();
    } catch { /* ignore */ }

    const poll = window.setInterval(() => {
      try {
        const t = localStorage.getItem('nexus-announce-tick') || '';
        if (t && t !== lastTick) {
          lastTick = t;
          hardReload();
        }
      } catch { /* ignore */ }
    }, 400);

    return () => {
      window.removeEventListener('storage', onStorage);
      window.clearInterval(poll);
      try { bc?.close(); } catch { /* ignore */ }
    };
  }, []);


  const branchOptions = useMemo(() => {
    const set = new Set(BRANCH_OPTIONS);
    tickets.forEach((t) => { if (t.branch) set.add(t.branch); });
    try {
      const raw = localStorage.getItem('nexus-branches-v1');
      if (raw) (JSON.parse(raw) as { name: string }[]).forEach((b) => set.add(b.name));
    } catch {}
    return Array.from(set).sort();
  }, [tickets]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim() || !title.trim() || !branch.trim()) {
      setError('Name, email, branch, and subject are required');
      return;
    }
    setSaving(true);
    setError('');
    try {
      const ticket = await createTicket({
        title: title.trim(), description: description.trim(), priority, channel: 'portal',
        customer_name: name.trim(), customer_email: email.trim(), branch: branch.trim(),
      });
      setCreated(ticket);
      setView('success');
      setTitle(''); setDescription(''); setPriority('medium');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Could not submit request');
    } finally {
      setSaving(false);
    }
  };

  const track = (e: React.FormEvent) => {
    e.preventDefault();
    setTrackError('');
    setTracked(null);
    setCsatDone(false);
    setCsatComment('');
    setCsatScore(5);
    const t = findTicket(trackId, trackEmail || user?.email || undefined);
    if (!t) {
      setTrackError('No ticket found. Check the ID and email you used when submitting.');
      return;
    }
    setTracked(t);
    setCsatDone(surveys.some((s) => s.ticket_id === t.id));
  };

  const submitCsat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tracked) return;
    setCsatSaving(true);
    try {
      await addSurvey({
        ticket_id: tracked.id,
        score: csatScore,
        comment: csatComment.trim() || undefined,
        customer_name: tracked.customer_name || name || undefined,
      });
      setCsatDone(true);
    } finally {
      setCsatSaving(false);
    }
  };

  const statusColor: Record<string, string> = {
    new: 'bg-violet-100 text-violet-700',
    open: 'bg-amber-100 text-amber-700',
    pending: 'bg-violet-100 text-violet-700',
    'on-hold': 'bg-zinc-100 text-zinc-600',
    resolved: 'bg-emerald-100 text-emerald-700',
  };

  const navItems: { id: PortalView; label: string; icon: typeof Home }[] = [
    { id: 'home', label: 'Overview', icon: Home },
    { id: 'community', label: 'Community', icon: Users },
    { id: 'submit', label: 'Submit request', icon: Ticket },
    { id: 'chat', label: 'Live chat', icon: MessageSquare },
    { id: 'track', label: 'Track ticket', icon: Search },
    { id: 'mytickets', label: 'My tickets', icon: User },
    { id: 'help', label: 'Help articles', icon: BookOpen },
    { id: 'account', label: 'Account', icon: User },
  ];

  const field =
    'w-full px-3 py-2 text-sm border border-zinc-200/70 rounded-lg bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 focus:bg-white/80 text-zinc-900 placeholder:text-zinc-400';
  const btnPrimary =
    'w-full py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors';

  if (!isCustomerSession) {
    return <PortalAuthGate onBackToAgent={onBackToAgent}>{null}</PortalAuthGate>;
  }

  return (
    <div className="app-cosmos flex h-screen max-h-screen overflow-hidden relative">
      <aside className="portal-sidebar hidden md:flex w-60 shrink-0 flex-col h-full max-h-screen overflow-hidden relative z-30">
        <div className="portal-sidebar-header px-4 py-5 flex items-center gap-3">
          <BrandMark />
          <div>
            <div className="text-sm font-semibold tracking-tight portal-sidebar-title">Nexus Ops</div>
            <div className="text-[11px] portal-sidebar-sub">Customer portal</div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider portal-sidebar-label">Support</div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = view === item.id || (view === 'success' && item.id === 'submit');
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setView(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  active ? 'portal-nav-active' : 'portal-nav-item'
                }`}
              >
                <Icon size={18} className={`shrink-0 ${({ home: "text-violet-700 dark:text-violet-300", community: "text-sky-600 dark:text-sky-400", submit: "text-amber-600 dark:text-amber-400", chat: "text-fuchsia-600 dark:text-fuchsia-400", track: "text-emerald-600 dark:text-emerald-400", mytickets: "text-blue-600 dark:text-blue-400", help: "text-indigo-700 dark:text-indigo-300", account: "text-pink-600 dark:text-pink-400" } as Record<string, string>)[item.id] || "text-violet-400"}`} />
                <span className="flex-1 text-left">{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="portal-sidebar-footer p-3 space-y-1">
          {onBackToAgent && (
            <button type="button" onClick={onBackToAgent} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-500 hover:bg-white/5 hover:text-zinc-200">
              <ExternalLink size={16} /> Agent desk
            </button>
          )}
          <div className="w-full flex items-center gap-3 px-3 py-2 rounded-lg">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xs font-semibold shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <div className="text-sm font-medium text-zinc-100 truncate">{displayName}</div>
              <div className="text-[11px] text-zinc-500 truncate">{user?.email}</div>
            </div>
          </div>
        </div>
      </aside>

      <div className="portal-shell flex-1 flex flex-col min-w-0 h-full max-h-full overflow-hidden relative z-10">
        <PortalSpaceLoungeBg />
        <header className="relative z-20 min-h-[3.75rem] shrink-0 nexus-topbar flex items-center gap-3 px-4 lg:px-6 py-2.5">
          <div className="md:hidden shrink-0"><BrandMark className="w-8 h-8" /></div>
          {(() => {
            const meta = VIEW_META[view];
            const NavIcon = navItems.find((n) => n.id === view)?.icon
              ?? (view === 'success' ? CheckCircle2 : Home);
            return (
              <div className="flex items-center gap-3 min-w-0">
                <div className={`w-10 h-10 rounded-xl bg-violet-500/10 dark:bg-violet-400/15 flex items-center justify-center shrink-0 ${meta.iconColor}`}>
                  <NavIcon size={20} strokeWidth={2.2} />
                </div>
                <div className="min-w-0">
                  <div className="text-base sm:text-lg font-semibold tracking-tight text-zinc-900 dark:text-zinc-50 leading-tight truncate">
                    {meta.title}
                  </div>
                  <div className="text-xs sm:text-[13px] text-zinc-500 dark:text-zinc-400 leading-snug truncate">
                    {meta.desc}
                  </div>
                </div>
              </div>
            );
          })()}
          <div className="flex-1" />
          <div className="hidden sm:flex items-center gap-2 text-xs text-zinc-500 dark:text-zinc-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Support online
          </div>
          <ThemeToggle />
          {requiresAuth && (
            <button
              type="button"
              onClick={() => void signOut()}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-violet-500/15 dark:hover:bg-white/10 border border-violet-700/25 dark:border-white/20 transition-colors"
              title="Sign out"
            >
              <LogOut size={15} strokeWidth={2.25} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          )}
        </header>

        <PortalAnnouncementMarquee />

        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 ${
            view === 'community' ? 'overflow-hidden flex flex-col' : 'overflow-y-auto'
          }`}
        >
          {/* Community fills space under marquee (no underlap). Other tabs: natural flow + footer after content. */}
          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1 flex-1'}>
            {view === 'home' && (
              <PortalHome displayName={displayName} onNavigate={(v) => setView(v)} />
            )}
            {view === 'community' && (
              <PortalCommunityChat displayName={displayName} email={user?.email || ''} onBack={() => setView('home')} />
            )}
            {view === 'chat' && <PortalLiveChat onBack={() => setView('home')} />}
            {view === 'submit' && (
              <div className="max-w-lg">
                <div className="mb-3">
                  <h1 className="text-lg font-semibold text-zinc-900 tracking-tight">Submit a request</h1>
                  <p className="text-zinc-500 text-sm mt-1">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{error}</div>}
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-zinc-600 mb-1.5">Your name *</label>
                      <input value={name} onChange={(e) => setName(e.target.value)} required className={field} />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-zinc-600 mb-1.5">Email *</label>
                      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required className={field} />
                    </div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Branch *</label>
                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="">Select branch…</option>
                      {branchOptions.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Subject *</label>
                    <input value={title} onChange={(e) => setTitle(e.target.value)} required className={field} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Details</label>
                    <textarea value={description} onChange={(e) => setDescription(e.target.value)} rows={4} className={field} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Priority</label>
                    <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className={field}>
                      {(['low', 'medium', 'high', 'critical'] as Priority[]).map((p) => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit request'}</button>
                </form>
              </div>
            )}
            {view === 'success' && created && (
              <div className="max-w-md text-center space-y-4 py-8">
                <CheckCircle2 className="mx-auto text-emerald-500" size={48} />
                <h1 className="text-xl font-semibold text-zinc-900">Request received</h1>
                <p className="text-zinc-500 text-sm">Your ticket ID is <span className="font-mono font-semibold text-violet-700">{created.id}</span>.</p>
                <div className="flex gap-2 justify-center">
                  <button type="button" onClick={() => { setTrackId(created.id); setView('track'); }} className="px-4 py-2 bg-brand-600 text-white text-sm font-medium rounded-lg hover:bg-brand-700">Track ticket</button>
                  <button type="button" onClick={() => setView('home')} className="px-4 py-2 border border-zinc-200 text-sm rounded-lg bg-white/80 hover:bg-white">Overview</button>
                </div>
              </div>
            )}
            {view === 'track' && (
              <div className="max-w-md">
                <h1 className="text-xl font-semibold text-zinc-900 mb-1">Track a ticket</h1>
                <form onSubmit={track} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3 mt-3">
                  {trackError && <div className="text-sm text-rose-600 bg-rose-50 px-3 py-2 rounded-lg">{trackError}</div>}
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Ticket ID</label>
                    <input value={trackId} onChange={(e) => setTrackId(e.target.value)} required className={field + ' font-mono'} placeholder="NX-2841" />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 mb-1.5">Email (optional)</label>
                    <input type="email" value={trackEmail} onChange={(e) => setTrackEmail(e.target.value)} placeholder={user?.email || ''} className={field} />
                  </div>
                  <button type="submit" className={btnPrimary}>Look up</button>
                </form>
                {tracked && (
                  <div className="mt-3 portal-glass-card rounded-xl p-4 space-y-2.5">
                    <div className="flex justify-between">
                      <span className="font-mono text-xs text-zinc-400">{tracked.id}</span>
                      <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${statusColor[tracked.status] || ''}`}>{tracked.status}</span>
                    </div>
                    <div className="font-semibold text-zinc-900">{tracked.title}</div>
                    <div className="text-xs text-zinc-500">{tracked.branch || 'No branch'} · {new Date(tracked.created_at).toLocaleString()}</div>
                    {tracked.status === 'resolved' && (
                      <div className="pt-3 border-t border-zinc-100">
                        {csatDone ? (
                          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2">Thanks for rating this support experience.</p>
                        ) : (
                          <form onSubmit={submitCsat} className="space-y-3">
                            <p className="text-sm font-medium text-zinc-800">How was our support?</p>
                            <div className="flex gap-1">
                              {[1, 2, 3, 4, 5].map((n) => (
                                <button key={n} type="button" onClick={() => setCsatScore(n)} className={`w-9 h-9 rounded-lg border text-sm font-semibold ${csatScore === n ? 'bg-violet-600 text-white border-violet-600' : 'bg-white text-zinc-600 border-zinc-200'}`}>{n}</button>
                              ))}
                            </div>
                            <textarea value={csatComment} onChange={(e) => setCsatComment(e.target.value)} rows={2} placeholder="Optional comment" className={field} />
                            <button type="submit" disabled={csatSaving} className={btnPrimary}>{csatSaving ? 'Sending…' : 'Submit rating'}</button>
                          </form>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
            {view === 'mytickets' && (
              <div className="max-w-2xl">
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">My tickets</h1>
                {myTickets.length === 0 ? (
                  <div className="rounded-xl border border-zinc-200 bg-white/80 px-4 py-3 text-sm text-zinc-500">No tickets linked to {user?.email} yet.</div>
                ) : (
                  <div className="space-y-2">
                    {myTickets.map((t) => (
                      <button key={t.id} type="button" onClick={() => { setTrackId(t.id); setTracked(t); setView('track'); }} className="w-full text-left rounded-xl border border-zinc-200 bg-white/80 px-4 py-3 hover:border-violet-300 transition-colors">
                        <div className="flex justify-between gap-2">
                          <span className="font-mono text-xs text-zinc-400">{t.id}</span>
                          <span className={`text-[10px] font-semibold px-1.5 py-0.5 rounded-full capitalize ${statusColor[t.status] || ''}`}>{t.status}</span>
                        </div>
                        <div className="font-medium text-zinc-900 mt-1">{t.title}</div>
                        <div className="text-xs text-zinc-500 mt-0.5">{t.branch || 'No branch'} · {new Date(t.created_at).toLocaleString()}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )}
            {view === 'help' && (
              <div className="max-w-2xl">
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">Help articles</h1>
                <div className="space-y-2">
                  {HELP_ARTICLES.map((a) => (
                    <div key={a.title} className="rounded-xl border border-zinc-200 bg-white/80 px-4 py-3">
                      <div className="font-medium text-zinc-900">{a.title}</div>
                      <p className="text-sm text-zinc-500 mt-1">{a.body}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {view === 'account' && (
              <div className="max-w-md">
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">Account</h1>
                <div className="rounded-xl border border-zinc-200 bg-white/80 p-4 space-y-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-sm font-semibold">{initials}</div>
                    <div>
                      <div className="font-medium text-zinc-900">{displayName}</div>
                      <div className="text-sm text-zinc-500">{user?.email}</div>
                    </div>
                  </div>
                  {requiresAuth && (
                    <button type="button" onClick={() => void signOut()} className="flex items-center justify-center gap-2 w-full py-2.5 text-sm font-medium text-zinc-700 border border-zinc-200 rounded-lg hover:bg-zinc-50">
                      <LogOut size={16} /> Sign out
                    </button>
                  )}
                </div>
              </div>
            )}
            </div>

            <footer className={`portal-footer relative z-10 shrink-0 px-2 py-3.5 rounded-xl ${
              view === 'community' ? 'mt-3 mb-1' : 'mt-auto mb-2 pt-6'
            }`}>
            <div className="text-center">
              <div className="text-[11px] sm:text-xs font-medium tracking-wide portal-footer-brand">
                NexusOps Customer Portal · © 2026 Lizer &amp; Kirzhian
              </div>
            </div>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}
