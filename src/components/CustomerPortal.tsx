/* workspace-switcher-portal-v1 */
/* view-detail-polish-v1 */
/* mytickets-menu-fixed-v1 */
/* status-colors-space-v1 */
/* portal-staff-preview-v1 */
/* portal-bell-v1 */
/* notif-z-expand-glass-v1 */
/* notif-above-marquee-v1 */
/* mytickets-wider-v1 */
/* mytickets-menu-guide-v1 */
/* mytickets-jsx-fix-v1 */
/* mytickets-actions-v1 */
/* mytickets-menu-anchor-v2 */
/* mytickets-menu-portal-v1 */
/* menu-page20-v1 */
/* mytickets-table-v1 */
/* followup-agent-notify-v1 */
/* fix-expand-fragment-v1 */
/* fix-cp-jsx-topbar-v1 */
/* expand-darker-glass-v1 */
/* details-tickets-theme-v1 */
/* customer-new-expand-v1 */
import { useState, useMemo, useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { ArrowLeft, BookOpen, CheckCircle2, ExternalLink, Home, Info, LogOut, MessageSquare, MoreVertical, Search, Send, Star, Ticket, User, Users } from 'lucide-react';
import { useTickets } from '../context/TicketContext';
import { useAuth } from '../context/AuthContext';
import { notifyAgents } from '../lib/agentNotify';
import { usePlatform } from '../context/PlatformContext';
import type { Priority, Ticket as TicketType, TicketAttachment } from '../types';
import { MAX_ATTACHMENT_BYTES } from '../types';
import { INITIAL_BRANCHES } from '../data';
import PortalLiveChat from './PortalLiveChat';
import PortalAuthGate from './PortalAuthGate';
import PortalHome from './PortalHome';
import PortalAnnouncementMarquee from './PortalAnnouncementMarquee';
import PortalCommunityChat from './PortalCommunityChat';
import ThemeToggle from './ThemeToggle';
import PortalSpaceLoungeBg from './PortalSpaceLoungeBg';

interface Props { onBackToAgent?: () => void; }
function capitalizeSentences(text: string): string {
  if (!text) return text;
  return text.replace(/(^|[.!?\n]\s+)([a-z])/g, (_m, lead: string, ch: string) => lead + ch.toUpperCase());
}

type PortalView = 'home' | 'submit' | 'track' | 'success' | 'help' | 'chat' | 'account' | 'mytickets' | 'community';

const HELP_ARTICLES = [
  { title: 'Reset your password', body: 'Go to Account → Sign in. Use the same email you registered with.' },
  { title: 'Check service status', body: 'Visit status.nexus.support for live incident updates before opening a ticket.' },
  { title: 'Billing & invoices', body: 'Invoices are emailed on the 1st of each month. Include your invoice number when submitting a request.' },
  { title: 'API rate limits', body: 'Free plans allow 60 requests/minute. Pro plans allow 600.' },
];

const BRANCH_OPTIONS = INITIAL_BRANCHES.map((b) => b.name);

/** Editable later — common ticket subjects for the portal form */
/** Subject list (alphabetical) — editable later */
const SUBJECT_OPTIONS = [
  'Access permissions / roles',
  'Account & login issues',
  'API access / API keys',
  'API rate limits',
  'Billing & invoices',
  'Branch or location change',
  'Bug report',
  'Data export or import',
  'Email delivery problems',
  'Feature request',
  'Hardware / device issue',
  'Integration help',
  'Mobile app issue',
  'Network connectivity',
  'Notifications & alerts',
  'Other',
  'Password reset / locked out',
  'Payment failed or declined',
  'Performance / slow response',
  'Security concern',
  'Service outage / downtime',
  'Subscription / plan change',
  'Training / how-to question',
] as const;


const VIEW_TITLES: Record<PortalView, string> = {
  home: 'Home',
  submit: 'Submit a request',
  track: 'Track a ticket',
  success: 'Request received',
  help: 'Help articles',
  chat: 'Live chat',
  account: 'Account',
  mytickets: 'My tickets',
  community: 'Community',
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

/* footer-flow-v2 */
/* labels-titlecase-v1 */ /* submit-form-v1 */ /* submit-layout-v1 */
/* nav-signout-v1 */ /* swap-signout-v1 */
/* submit-guide-v1 */
/* submit-left-subject-v1 */
/* submit-success-modal-v1 */
export default function CustomerPortal({ onBackToAgent }: Props) {
  const { createTicket, updateTicket, findTicket, tickets, ticketsForEmail } = useTickets();
  const { user, accountRole, signOut, requiresAuth } = useAuth();
  const {
    addSurvey,
    surveys,
    notifications,
    unreadCount: platformUnread,
    markNotificationRead,
    markAllNotificationsRead,
    conversations,
  } = usePlatform();
  const [view, setView] = useState<PortalView>('home');
  const [myTicketsPage, setMyTicketsPage] = useState(1);
  const [myTicketsDateFrom, setMyTicketsDateFrom] = useState('');
  const [myTicketsDateTo, setMyTicketsDateTo] = useState('');
  const [myTicketMenuId, setMyTicketMenuId] = useState<string | null>(null);
  const [myTicketMenuPos, setMyTicketMenuPos] = useState<{ top: number; left: number; openUp: boolean }>({
    top: 0,
    left: 0,
    openUp: false,
  });
  const [followUpTicket, setFollowUpTicket] = useState<TicketType | null>(null);
  const [followUpText, setFollowUpText] = useState('');
  const [followUpBusy, setFollowUpBusy] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [branch, setBranch] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<Priority | ''>('');
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
    if (!user) return;
    // Locked identity — always mirror the registered account name (prevents shared-account spoofing)
    const display =
      (user.user_metadata?.full_name as string)?.trim() ||
      user.email?.split('@')[0] ||
      'Customer';
    setName(display);
    if (user.email) setEmail(user.email);
  }, [user]);


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
        title: title.trim(), description: capitalizeSentences(description.trim()), priority, channel: 'portal',
        customer_name: name.trim(), customer_email: email.trim(), branch: branch.trim(),
      });
      setCreated(ticket);
      setView('success');
      setTitle(''); setDescription(''); setPriority('');
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
    new: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    open: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    pending: 'bg-orange-100 text-orange-800 dark:bg-orange-500/25 dark:text-orange-200 border border-orange-300/60 dark:border-orange-400/40',
    'on-hold': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-500/25 dark:text-yellow-100 border border-yellow-300/60 dark:border-yellow-400/40',
    resolved: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/25 dark:text-emerald-200 border border-emerald-300/60 dark:border-emerald-400/40',
    closed: 'bg-red-100 text-red-800 dark:bg-red-500/25 dark:text-red-200 border border-red-300/60 dark:border-red-400/40',
  };

  const navItems: { id: PortalView; label: string; icon: typeof Home }[] = [
    { id: 'home', label: 'Overview', icon: Home },
    { id: 'community', label: 'Community', icon: Users },
    { id: 'submit', label: 'Submit a Ticket', icon: Ticket },
    { id: 'chat', label: 'Live Chat', icon: MessageSquare },
    { id: 'track', label: 'Track Ticket', icon: Search },
    { id: 'mytickets', label: 'My Tickets', icon: User },
    { id: 'help', label: 'Help Articles', icon: BookOpen },
    { id: 'account', label: 'Account', icon: User },
  ];

  const field =
    'w-full px-3 py-2 text-sm border border-zinc-200/70 rounded-lg bg-white/50 backdrop-blur-sm focus:outline-none focus:ring-2 focus:ring-violet-500/25 focus:border-violet-400 focus:bg-white/80 text-zinc-900 placeholder:text-zinc-400';
  const btnPrimary =
    'w-full py-2.5 bg-brand-600 text-white text-sm font-semibold rounded-lg hover:bg-brand-700 disabled:opacity-50 transition-colors';

  const portalNotifs = useMemo(() => {
    const items: {
      id: string;
      title: string;
      body?: string;
      link: PortalView;
      read: boolean;
      created_at: string;
      kind: 'platform' | 'ticket' | 'chat';
      ticketId?: string;
    }[] = [];
    for (const n of notifications) {
      const linkRaw = (n.link || '').toLowerCase();
      let link: PortalView = 'mytickets';
      if (linkRaw.includes('chat') || linkRaw.includes('live')) link = 'chat';
      else if (linkRaw.includes('ticket') || linkRaw.includes('myticket')) link = 'mytickets';
      items.push({
        id: n.id,
        title: n.title,
        body: n.body,
        link,
        read: !!n.read,
        created_at: n.created_at,
        kind: 'platform',
      });
    }
    for (const t of myTickets) {
      if (!(t.tags || []).includes('customer_unread')) continue;
      items.push({
        id: `ticket-${t.id}`,
        title: 'Ticket updated',
        body: t.title || t.id,
        link: 'mytickets',
        read: false,
        created_at: t.updated_at || t.created_at,
        kind: 'ticket',
        ticketId: t.id,
      });
    }
    const email = (user?.email || '').toLowerCase();
    for (const conv of conversations) {
      if (!email) continue;
      const cust = ((conv as { customer_email?: string }).customer_email || '').toLowerCase();
      const blob = JSON.stringify(conv).toLowerCase();
      if (cust !== email && !blob.includes(email)) continue;
      if (conv.status === 'ended') continue;
      const msgs = conv.messages || [];
      const last = msgs[msgs.length - 1];
      if (!last || last.sender !== 'agent') continue;
      items.push({
        id: `chat-${conv.id}`,
        title: 'New live chat message',
        body: (last.text || '').slice(0, 120),
        link: 'chat',
        read: false,
        created_at: last.created_at || (conv as { updated_at?: string }).updated_at || new Date().toISOString(),
        kind: 'chat',
      });
    }
    items.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    const seen = new Set<string>();
    return items.filter((x) => {
      if (seen.has(x.id)) return false;
      seen.add(x.id);
      return true;
    });
  }, [notifications, myTickets, conversations, user?.email]);

  const portalUnread = portalNotifs.filter((n) => !n.read).length;

  const openPortalNotif = async (n: (typeof portalNotifs)[0]) => {
    setPortalNotifOpen(false);
    if (n.kind === 'platform') {
      void markNotificationRead(n.id);
    }
    if (n.kind === 'ticket' && n.ticketId) {
      const t = myTickets.find((x) => x.id === n.ticketId);
      if (t) {
        void updateTicket(t.id, {
          tags: (t.tags || []).filter((x) => x !== 'customer_unread'),
        });
        setExpandedTicketId(t.id);
      }
    }
    setView(n.link);
  };


  /* Staff (agent/admin) may preview the portal; customers use full session.
     Previously non-customers rendered null → blank white page on #portal. */
  if (requiresAuth && !user) {
    return null;
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
            <button
              type="button"
              onClick={onBackToAgent}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-violet-800 dark:text-violet-100 bg-violet-100/90 dark:bg-violet-500/20 border border-violet-400/40 hover:bg-violet-200 dark:hover:bg-violet-500/30"
            >
              <ExternalLink size={16} /> Agent Workspace
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
        <header className="relative z-20 h-12 shrink-0 nexus-topbar flex items-center gap-3 px-4 lg:px-6">
          <div className="md:hidden"><BrandMark className="w-8 h-8" /></div>
          <div className="text-sm font-semibold text-zinc-800">{VIEW_TITLES[view]}</div>
          <div className="flex-1" />
          <div className="hidden sm:flex items-center gap-2 text-xs text-zinc-500">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            Support online
          </div>
          <ThemeToggle />
          {requiresAuth && (
                          {onBackToAgent && (
                <button
                  type="button"
                  onClick={onBackToAgent}
                  className="switch-to-agent-top inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 border border-violet-500/50 shadow-md"
                  title="Back to Agent Workspace"
                >
                  <ExternalLink size={14} />
                  <span className="hidden sm:inline">Agent Workspace</span>
                </button>
              )}
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
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 flex flex-col ${
            view === 'community' ? 'overflow-hidden' : 'overflow-y-auto'
          }`}
        >
          <div
            className={`w-full mx-auto flex flex-col flex-1 min-h-0 ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={`flex-1 min-h-0 ${view === 'community' ? 'flex flex-col' : ''}`}>
            {view === 'home' && (
              <PortalHome displayName={displayName} onNavigate={(v) => setView(v)} />
            )}
            {view === 'community' && (
              <PortalCommunityChat displayName={displayName} email={user?.email || ''} onBack={() => setView('home')} />
            )}
            {view === 'chat' && <PortalLiveChat onBack={() => setView('home')} />}
            {view === 'submit' && (
              <div className="w-full flex flex-col lg:flex-row lg:items-start gap-6 lg:gap-8">
                <div className="w-full max-w-md shrink-0 self-start">
                <div className="mb-4">
                  <h1 className="text-2xl sm:text-3xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">Submit a Ticket</h1>
                  <p className="text-zinc-500 dark:text-zinc-400 text-sm sm:text-base mt-1.5">We typically respond within one business day.</p>
                </div>
                <form onSubmit={submit} className="portal-glass-card rounded-xl p-4 sm:p-5 space-y-3.5 relative z-20">
                  {error && <div className="text-sm text-rose-600 bg-rose-50 dark:bg-rose-950/40 dark:text-rose-300 px-3 py-2 rounded-lg">{error}</div>}
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Your name</label>
                    <input
                      value={name}
                      readOnly
                      required
                      className={`${field} opacity-90 cursor-not-allowed bg-zinc-100/80 dark:bg-white/5`}
                      title="Filled from your account — cannot be changed"
                    />
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Locked to your registered account name.</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Branch *</label>
                    <select value={branch} onChange={(e) => setBranch(e.target.value)} required className={field}>
                      <option value="">Select branch…</option>
                      {branchOptions.map((b) => <option key={b} value={b}>{b}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Subject *</label>
                    <select value={title} onChange={(e) => setTitle(e.target.value)} required className={field}>
                      <option value="" disabled>
                        Select a request type…
                      </option>
                      {SUBJECT_OPTIONS.map((s) => (
                        <option key={s} value={s}>{s}</option>
                      ))}
                    </select>
                    <p className="text-[11px] text-zinc-500 dark:text-zinc-400 mt-1">Choose the closest match — you can clarify in Details.</p>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Details</label>
                    <textarea
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      rows={4}
                      placeholder="Describe what happened, steps to reproduce, and any error messages…"
                      className={field}
                    />
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <label className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-violet-700 dark:text-violet-300 bg-violet-500/10 hover:bg-violet-500/15 border border-violet-500/20 cursor-pointer transition-colors">
                        <ImagePlus size={14} />
                        {attachPreview ? 'Change photo' : 'Add photo'}
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.target.value = '';
                            setAttachError('');
                            if (!file) return;
                            if (!file.type.startsWith('image/')) {
                              setAttachError('Please choose an image file.');
                              return;
                            }
                            if (file.size > MAX_ATTACHMENT_BYTES) {
                              setAttachError('Image is too large (max 8 MB).');
                              return;
                            }
                            const reader = new FileReader();
                            reader.onload = () => {
                              setAttachPreview({
                                name: file.name,
                                size: file.size,
                                mime: file.type,
                                url: String(reader.result || ''),
                              });
                            };
                            reader.onerror = () => setAttachError('Could not read that image.');
                            reader.readAsDataURL(file);
                          }}
                        />
                      </label>
                      <span className="text-[11px] text-zinc-500 dark:text-zinc-400">Optional · max 8 MB</span>
                      {attachPreview && (
                        <button
                          type="button"
                          onClick={() => { setAttachPreview(null); setAttachError(''); }}
                          className="inline-flex items-center gap-1 text-[11px] text-zinc-600 dark:text-zinc-300 hover:text-rose-600"
                        >
                          <X size={12} /> Remove
                        </button>
                      )}
                    </div>
                    {attachError && <p className="text-[11px] text-rose-600 mt-1">{attachError}</p>}
                    {attachPreview && (
                      <div className="mt-2 rounded-lg overflow-hidden border border-zinc-200 dark:border-white/10 max-w-xs">
                        <img src={attachPreview.url} alt={attachPreview.name} className="max-h-36 w-full object-contain bg-black/5" />
                        <div className="px-2 py-1 text-[10px] text-zinc-500 truncate">{attachPreview.name}</div>
                      </div>
                    )}
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-zinc-600 dark:text-zinc-300 mb-1.5">Priority</label>
                    <select value={priority} onChange={(e) => setPriority(e.target.value as Priority)} className={field}>
                      {([
                        { value: 'low', label: 'Low' },
                        { value: 'medium', label: 'Medium' },
                        { value: 'high', label: 'High' },
                        { value: 'critical', label: 'Critical' },
                      ] as { value: Priority; label: string }[]).map((p) => (
                        <option key={p.value} value={p.value}>{p.label}</option>
                      ))}
                    </select>
                  </div>
                  <button type="submit" disabled={saving} className={btnPrimary}>{saving ? 'Submitting…' : 'Submit a Ticket'}</button>
                </form>
                </div>
                {/* Right column reserved for upcoming Submit Ticket panel content */}
                <div className="flex-1 min-w-0 hidden lg:block" aria-hidden="true" />
              </div>
            )}
            {created && (
              <div
                className="fixed inset-0 z-[80] flex items-center justify-center p-4"
                role="dialog"
                aria-modal="true"
                aria-labelledby="ticket-received-title"
              >
                <button
                  type="button"
                  className="absolute inset-0 bg-black/50 backdrop-blur-[2px]"
                  aria-label="Close"
                  onClick={() => setCreated(null)}
                />
                <div className="relative w-full max-w-sm rounded-2xl border border-white/20 dark:border-white/10 bg-white/95 dark:bg-zinc-900/95 shadow-2xl shadow-violet-950/30 px-6 py-7 text-center space-y-4">
                  <div className="mx-auto w-14 h-14 rounded-full bg-emerald-500/15 flex items-center justify-center">
                    <CheckCircle2 className="text-emerald-500" size={36} strokeWidth={2} />
                  </div>
                  <div>
                    <h2 id="ticket-received-title" className="text-xl font-semibold text-zinc-900 dark:text-zinc-50 tracking-tight">
                      Request received
                    </h2>
                    <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-300 leading-relaxed">
                      Your ticket ID is{' '}
                      <span className="font-mono font-semibold text-violet-700 dark:text-violet-300">{created.id}</span>.
                    </p>
                    <p className="mt-1.5 text-xs text-zinc-500 dark:text-zinc-400">
                      We typically respond within one business day. You can track status anytime.
                    </p>
                  </div>
                  <div className="flex flex-col sm:flex-row gap-2 justify-center pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        setTrackId(created.id);
                        setCreated(null);
                        setView('track');
                      }}
                      className="px-4 py-2.5 bg-brand-600 text-white text-sm font-medium rounded-xl hover:bg-brand-700 transition-colors"
                    >
                      Track Ticket
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setCreated(null);
                        setView('home');
                      }}
                      className="px-4 py-2.5 border border-zinc-200 dark:border-white/15 text-sm rounded-xl bg-white/80 dark:bg-white/5 text-zinc-800 dark:text-zinc-100 hover:bg-white dark:hover:bg-white/10 transition-colors"
                    >
                      Overview
                    </button>
                  </div>
                  <button
                    type="button"
                    onClick={() => setCreated(null)}
                    className="text-xs text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300 underline-offset-2 hover:underline"
                  >
                    Stay on Submit a Ticket
                  </button>
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
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">My Tickets</h1>
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
                <h1 className="text-xl font-semibold text-zinc-900 mb-3">Help Articles</h1>
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

            <footer className="portal-footer relative z-10 mt-auto shrink-0 mb-1 px-2 py-3.5 rounded-xl">
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
