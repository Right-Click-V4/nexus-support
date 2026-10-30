/* portal-force-ready-v1 */
/* presence-fast-online-v1 */
/* toast-created-window-v1 */
/* portal-postlogin-fix-v1 */
/* login-customer-first-v1 */
/* presence-heartbeat-v1 */
/* agent-presence-shell-v1 */
/* agent-notif-nav-v1 */
/* toast-hydrate-v1 */
/* agent-toast-polish-v1 */
/* agent-toast-from-notif-v1 */
/* followup-agent-toast-v1 */
/* workspace-switcher-v1 */
/* agent-topbar-icons-v1 */
/* agent-chrome-meta-v1 */
/* agent-topbar-right-v1 */
/* tickets-badge-unread-v1 */
import { useEffect, useRef, useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import TicketsPage from './components/TicketsPage';
import CustomersPage from './components/CustomersPage';
import TeamPage from './components/TeamPage';
import AnalyticsPage from './components/AnalyticsPage';
import KnowledgePage from './components/KnowledgePage';
import LiveChatPage from './components/LiveChatPage';
import AutomationsPage from './components/AutomationsPage';
import MacrosPage from './components/MacrosPage';
import SurveysPage from './components/SurveysPage';
import UsersAdminPage from './components/UsersAdminPage';
import QualityPage from './components/QualityPage';
import AnnouncementsPage from './components/AnnouncementsPage';
import FormsPage from './components/FormsPage';
import ReleasesPage from './components/ReleasesPage';
import SettingsPage from './components/SettingsPage';
import ProfilePage from './components/ProfilePage';
import LoginPage from './components/LoginPage';
import CustomerPortal from './components/CustomerPortal';
import PortalAuthGate from './components/PortalAuthGate';
import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn, clearJustLoggedIn } from './components/PostLoginLoader';
import AdminFeaturesPage from './components/AdminFeaturesPage';
import MaintenanceScreen from './components/MaintenanceScreen';
import NotFoundScreen from './components/NotFoundScreen';
import { TicketProvider, useTickets } from './context/TicketContext';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { MaintenanceProvider, useMaintenance } from './context/MaintenanceContext';
import { Site404Provider, useSite404 } from './context/Site404Context';
import { useIsAdmin } from './components/useIsAdmin';
import {
  Bell,
  Settings,
  ExternalLink,
  LayoutDashboard,
  Ticket,
  Building2,
  Users,
  UserCog,
  BarChart3,
  BookOpen,
  MessageSquare,
  Zap,
  FileText,
  ClipboardList,
  Award,
  Megaphone,
  FormInput,
  Rocket,
  User,
  Shield,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import AgentAvatar from './components/AgentAvatar';
import ThemeToggle from './components/ThemeToggle';
import { onAgentNotify } from './lib/agentNotify';

export function getModeFromHash(): 'agent' | 'portal' | 'notfound' {
  const h = (window.location.hash || '').replace(/^#/, '').toLowerCase().split('?')[0];
  if (h === '404' || h === 'not-found' || h === 'notfound') return 'notfound';
  if (h.startsWith('portal')) return 'portal';
  if (h && !h.startsWith('portal') && !['', 'agent', 'app', 'desk'].includes(h) && h.includes('/')) {
    return 'notfound';
  }
  return 'agent';
}

const TITLES: Record<string, string> = {
  dashboard: 'Overview',
  tickets: 'Tickets',
  customers: 'Branches',
  team: 'Team',
  users: 'Users & access',
  analytics: 'Analytics',
  knowledge: 'Knowledge Base',
  chat: 'Live Chat',
  automations: 'Automations',
  macros: 'Macros',
  surveys: 'Surveys',
  quality: 'Quality',
  announcements: 'Announcements',
  forms: 'Forms',
  releases: 'Releases',
  settings: 'Settings',
  profile: 'Profile',
  'admin-features': 'Admin features',
};

const VIEW_META: Record<string, { title: string; description: string }> = {
  dashboard: { title: 'Overview', description: 'Workspace snapshot — open work, breaches, and quick actions.' },
  tickets: { title: 'Tickets', description: 'Triage, assign, and resolve support tickets from every channel.' },
  customers: { title: 'Branches', description: 'Branch locations and related customer context.' },
  team: { title: 'Team', description: 'Agents on the desk — presence, roles, and coverage.' },
  users: { title: 'Users & access', description: 'Accounts, roles, and who can sign in to the workspace.' },
  analytics: { title: 'Analytics', description: 'Volume, SLA, and performance trends across tickets.' },
  knowledge: { title: 'Knowledge Base', description: 'Articles and answers agents use while helping customers.' },
  chat: { title: 'Live Chat', description: 'Real-time conversations with customers who need help now.' },
  automations: { title: 'Automations', description: 'Rules that route, tag, or escalate work without manual steps.' },
  macros: { title: 'Macros', description: 'Reusable replies and actions for common ticket updates.' },
  surveys: { title: 'Surveys', description: 'Collect feedback after tickets close.' },
  quality: { title: 'Quality', description: 'Review conversations and coaching signals.' },
  announcements: { title: 'Announcements', description: 'Publish marquee and portal messages for customers.' },
  forms: { title: 'Forms', description: 'Structured intake forms tied to ticket workflows.' },
  releases: { title: 'Releases', description: 'Product and ops release notes shared with the team.' },
  settings: { title: 'Settings', description: 'Workspace preferences, channels, and configuration.' },
  profile: { title: 'Profile', description: 'Your agent profile, avatar, and personal preferences.' },
  'admin-features': { title: 'Admin features', description: 'Admin-only tools for platform control and maintenance.' },
};

const NAV_ICONS: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  tickets: Ticket,
  customers: Building2,
  team: Users,
  users: UserCog,
  analytics: BarChart3,
  knowledge: BookOpen,
  chat: MessageSquare,
  automations: Zap,
  macros: FileText,
  surveys: ClipboardList,
  quality: Award,
  announcements: Megaphone,
  forms: FormInput,
  releases: Rocket,
  settings: Settings,
  profile: User,
  'admin-features': Shield,
};

export function AgentShell() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [notifOpen, setNotifOpen] = useState(false);
  const [agentToast, setAgentToast] = useState<{ title: string; body: string } | null>(null);
  const prevNotifIdsRef = useRef<Set<string>>(new Set());
  const toastBootRef = useRef(true);
  const notifRef = useRef<HTMLDivElement>(null);
  const { tickets, usingSupabase, currentAgent, updateAgentStatus: setPresenceStatus, touchPresence } = useTickets();
  const presenceAgent = currentAgent;
  const { user, loading: authLoading, authBusy, requiresAuth, signOut, accountRole } = useAuth();
  const { enabled: maintenanceOn, ready: maintenanceReady } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const [adminLogin, setAdminLogin] = useState(false);
  const {
    notifications,
    unreadCount,
    refreshPlatform,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    deleteAllNotifications,
    conversations,
  } = usePlatform();


  /* Toast only for notifs that arrive AFTER initial hydrate (avoid spam on refresh) */

  /* Presence: workspace open → online + heartbeat; last tab / logout → offline */
  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') {
      void setPresenceStatus('online');
    } else {
      void touchPresence?.();
    }
    void touchPresence?.();
    const quick = window.setTimeout(() => { void touchPresence?.(); }, 500);
    return () => window.clearTimeout(quick);
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => { void touchPresence?.(); };
    tick();
    const id = window.setInterval(tick, 5000);
    return () => window.clearInterval(id);
  }, [presenceAgent?.id, touchPresence]);

  useEffect(() => {
    const goOffline = () => {
      try { void setPresenceStatus('offline'); } catch { /* ignore */ }
    };
    const onPageHide = () => {
      try {
        const raw = localStorage.getItem('nexus-live-tabs-v3');
        const tabs = raw ? JSON.parse(raw) : {};
        const now = Date.now();
        const live = Object.entries(tabs || {}).filter(
          ([, ts]) => typeof ts === 'number' && now - (ts as number) < 8000,
        );
        if (live.length <= 1) goOffline();
      } catch {
        goOffline();
      }
    };
    window.addEventListener('pagehide', onPageHide);
    return () => window.removeEventListener('pagehide', onPageHide);
  }, [setPresenceStatus]);

  useEffect(() => {
    const ids = new Set(notifications.map((n) => n.id));
    if (toastBootRef.current) {
      prevNotifIdsRef.current = new Set([...prevNotifIdsRef.current, ...ids]);
      const settle = window.setTimeout(() => {
        prevNotifIdsRef.current = new Set(notifications.map((n) => n.id));
        toastBootRef.current = false;
      }, 3500);
      return () => window.clearTimeout(settle);
    }
    const isCustomerOrigin = (n: { title?: string; body?: string; link?: string; created_at?: string }) => {
      const t = (n.title || '').toLowerCase();
      const b = (n.body || '').toLowerCase();
      const link = (n.link || '').toLowerCase();
      if (/ticket updated/.test(t)) return false;
      if (/new ticket/.test(t)) return true;
      if (/follow-?up/.test(t) || /follow-?up/.test(b)) return true;
      if (/live\s*chat|customer message|new message/.test(t) || /live\s*chat/.test(b)) return true;
      if (link === 'chat' || link === 'livechat') return true;
      return false;
    };
    const isRecent = (n: { created_at?: string }) => {
      if (!n.created_at) return false;
      const age = Date.now() - new Date(n.created_at).getTime();
      return !Number.isNaN(age) && age >= 0 && age < 45_000;
    };
    const fresh = notifications.filter(
      (n) =>
        !prevNotifIdsRef.current.has(n.id) &&
        !n.read &&
        isCustomerOrigin(n) &&
        isRecent(n),
    );
    prevNotifIdsRef.current = ids;
    if (fresh.length === 0) return;
    const latest = fresh[0];
    setAgentToast({
      title: latest.title || 'New notification',
      body: latest.body || '',
    });
    const t = window.setTimeout(() => setAgentToast(null), 7000);
    return () => window.clearTimeout(t);
  }, [notifications]);

  useEffect(() => {
    const onEvt = (e: Event) => {
      const detail = (e as CustomEvent).detail;
      let title = 'Follow-up requested';
      let body = 'A customer asked for an update on their ticket.';
      if (detail && !Array.isArray(detail) && detail.title) {
        title = detail.title;
        body = detail.body || body;
      } else if (Array.isArray(detail) && detail[0]?.title) {
        title = detail[0].title;
        body = detail[0].body || body;
      } else {
        try {
          const raw = localStorage.getItem('nexus-notif-v1');
          const list = raw ? JSON.parse(raw) : [];
          if (Array.isArray(list) && list[0]?.title) {
            title = list[0].title;
            body = list[0].body || body;
          }
        } catch { /* ignore */ }
      }
      const tLow = title.toLowerCase();
      const bLow = (body || '').toLowerCase();
      const customer =
        /new ticket/.test(tLow) ||
        /follow-?up/.test(tLow) ||
        /follow-?up/.test(bLow) ||
        /live\s*chat|customer message|new message/.test(tLow);
      if (!customer) return;
      setAgentToast({ title, body });
      window.setTimeout(() => setAgentToast(null), 7000);
      void refreshPlatform?.();
    };
    window.addEventListener('nexus-agent-notify', onEvt);
    return () => window.removeEventListener('nexus-agent-notify', onEvt);
  }, [refreshPlatform]);

  /* Badge: New or unopened (unread tag) tickets only — clears when agent opens the ticket */
  const openCount = tickets.filter(
    (t) =>
      !t.deleted_at &&
      (t.status === 'new' || (t.tags || []).includes('unread'))
  ).length;
  const chatBadge = conversations.filter((c) => c.status !== 'ended').length;
  const displayName =
    currentAgent?.name ||
    (user?.user_metadata?.full_name as string | undefined) ||
    user?.email?.split('@')[0] ||
    'Agent';

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  if (requiresAuth && authLoading && !authBusy) {
    return <BootLoader label="Loading workspace…" />;
  }

  if (!maintenanceReady || !site404Ready) {
    return <BootLoader label="Loading…" />;
  }

  const admin = accountRole === 'admin' || isAdmin || !!currentAgent?.is_admin;

  if (maintenanceOn && !admin) {
    if (adminLogin || authBusy) {
      return (
        <LoginPage
          audience="agent"
          onOpenPortal={() => {
            window.location.hash = 'portal';
          }}
        />
      );
    }
    if (user && !adminReady) {
      return <BootLoader label="Checking access…" />;
    }
    return (
      <MaintenanceScreen
        onAdminSignIn={!user ? () => setAdminLogin(true) : undefined}
      />
    );
  }

  if (site404On && !admin) {
    if (adminLogin || authBusy) {
      return (
        <LoginPage
          audience="agent"
          onOpenPortal={() => {
            window.location.hash = 'portal';
          }}
        />
      );
    }
    if (user && !adminReady) {
      return <BootLoader label="Checking access…" />;
    }
    return (
      <NotFoundScreen
        onAdminSignIn={!user ? () => setAdminLogin(true) : undefined}
        onGoHome={() => {
          window.location.hash = '';
        }}
      />
    );
  }

  if (requiresAuth && (!user || authBusy)) {
    return (
      <LoginPage
        audience="customer"
        onOpenPortal={() => {
          window.location.hash = 'portal';
        }}
      />
    );
  }

  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) {
      window.location.hash = 'portal';
    }
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Opening customer portal…" />;
  }

  const agentReady = !requiresAuth || (!!user && accountRole !== 'customer' && !authLoading && !authBusy);

  return (
    <PostLoginShell ready={agentReady} label="Opening agent workspace…" variant="agent">
      
      {agentToast && (
        <div
          className="agent-toast-followup fixed z-[9999] max-w-sm w-[min(100vw-2rem,22rem)] rounded-xl border px-4 py-3 shadow-2xl backdrop-blur-md
            top-[4.25rem] right-4
            border-violet-300/50 bg-white/80 text-zinc-900
            dark:border-violet-400/35 dark:bg-zinc-900/75 dark:text-zinc-50
            animate-agent-toast-in cursor-pointer"
          role="status"
          onClick={() => {
            const t = (agentToast.title || '').toLowerCase();
            const b = (agentToast.body || '').toLowerCase();
            if (/live\s*chat|customer message|new message/.test(t) || /live\s*chat/.test(b)) {
              setActiveNav('chat');
            } else {
              setActiveNav('tickets');
            }
            setAgentToast(null);
          }}
        >
          <div className="flex items-start gap-3">
            <div className="mt-0.5 w-8 h-8 rounded-lg bg-violet-500/20 text-violet-700 dark:bg-violet-500/25 dark:text-violet-200 flex items-center justify-center shrink-0">
              <Bell size={16} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-semibold leading-snug text-zinc-900 dark:text-white">{agentToast.title}</div>
              <div className="text-xs text-zinc-600 dark:text-zinc-300 mt-1 whitespace-pre-line leading-relaxed">{agentToast.body}</div>
            </div>
            <button
              type="button"
              onClick={() => setAgentToast(null)}
              className="text-zinc-400 hover:text-zinc-800 dark:hover:text-white text-lg leading-none px-1"
              aria-label="Dismiss"
            >
              ×
            </button>
          </div>
        </div>
      )}

      <div className="app-cosmos flex min-h-screen">
        <Sidebar
          active={activeNav}
          onNavigate={setActiveNav}
          openCount={openCount}
          chatBadge={chatBadge}
          displayName={displayName}
          avatarUrl={currentAgent?.avatar_url || (user?.user_metadata?.avatar_url as string | undefined) || null}
          agentStatus={currentAgent?.status || 'online'}
          onProfile={() => setActiveNav('profile')}
          isAdmin={admin}
        />
        <div className="flex-1 flex flex-col min-w-0 min-h-screen">
          <header className="nexus-topbar relative z-40 min-h-[3.75rem] h-auto py-2.5 shrink-0 flex items-center gap-3 px-4 lg:px-6 xl:px-8 w-full">
            <div className="shrink-0 min-w-0 max-w-[min(32rem,55%)] pr-3 flex items-start gap-3">
              {(() => {
                const Icon = NAV_ICONS[activeNav] || LayoutDashboard;
                return (
                  <div className="mt-0.5 w-10 h-10 rounded-xl bg-violet-500/15 text-violet-700 dark:bg-violet-400/20 dark:text-violet-200 flex items-center justify-center shrink-0 border border-violet-400/30">
                    <Icon size={20} strokeWidth={2.25} />
                  </div>
                );
              })()}
              <div className="min-w-0">
                <div className="text-lg sm:text-xl font-bold tracking-tight text-zinc-900 dark:text-white leading-tight truncate">
                  {(VIEW_META[activeNav] || { title: TITLES[activeNav] || activeNav }).title}
                </div>
                <p className="text-[11px] sm:text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5 line-clamp-2">
                  {(VIEW_META[activeNav] || { description: '' }).description}
                </p>
              </div>
            </div>
            <div className="flex-1 min-w-0" aria-hidden />
            <div className="flex items-center gap-1 sm:gap-2 shrink-0 ml-auto">
                            {(accountRole === 'agent' || accountRole === 'admin' || admin) && (
                <button
                  type="button"
                  onClick={() => {
                    window.location.hash = 'portal';
                  }}
                  className="inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg border border-violet-700/40 bg-violet-600 hover:bg-violet-700 shadow-md shadow-violet-600/25 transition-colors"
                  title="Preview Customer Portal"
                >
                  <ExternalLink size={14} className="text-white" />
                  <span className="hidden sm:inline">Customer Portal</span>
                </button>
              )}
              <ThemeToggle />
              <div className="relative z-[50]" ref={notifRef}>
                <button
                  type="button"
                  onClick={() => setNotifOpen((v) => !v)}
                  className="relative p-2 rounded-lg text-zinc-500 hover:bg-zinc-100 hover:text-zinc-800"
                >
                  <Bell size={18} />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-rose-500 text-white text-[10px] font-semibold flex items-center justify-center">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>
                {notifOpen && (
                  <div className="absolute right-0 top-full mt-1 w-80 max-h-96 overflow-auto rounded-xl border border-zinc-200 bg-white shadow-2xl z-[9999]">
                    <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-100 sticky top-0 bg-white">
                      <span className="text-xs font-semibold text-zinc-700">Notifications</span>
                      <div className="flex gap-2">
                        <button type="button" className="text-[11px] text-violet-600" onClick={() => void markAllNotificationsRead()}>
                          Read all
                        </button>
                        <button type="button" className="text-[11px] text-zinc-400" onClick={() => void deleteAllNotifications()}>
                          Clear
                        </button>
                      </div>
                    </div>
                    {notifications.length === 0 ? (
                      <div className="px-3 py-6 text-center text-xs text-zinc-400">No notifications</div>
                    ) : (
                      notifications.slice(0, 30).map((n) => (
                        <div
                          key={n.id}
                          className={`px-3 py-2.5 border-b border-zinc-50 text-xs ${n.read ? 'opacity-60' : 'bg-violet-50/40'}`}
                        >
                          <div className="flex justify-between gap-2">
                            <button
                              type="button"
                              className="text-left flex-1"
                              onClick={() => {
                                void markNotificationRead(n.id);
                                setNotifOpen(false);
                                const link = (n.link || '').toLowerCase();
                                const title = (n.title || '').toLowerCase();
                                const body = (n.body || '').toLowerCase();
                                if (
                                  link === 'chat' ||
                                  link === 'livechat' ||
                                  /live\s*chat|customer message|new message/.test(title) ||
                                  /live\s*chat/.test(body)
                                ) {
                                  setActiveNav('chat');
                                } else if (
                                  link === 'tickets' ||
                                  link === 'ticket' ||
                                  /ticket|follow-?up|new ticket/.test(title) ||
                                  /ticket|follow-?up/.test(body)
                                ) {
                                  setActiveNav('tickets');
                                } else if (link === 'dashboard' || link === 'overview') {
                                  setActiveNav('dashboard');
                                } else if (link) {
                                  setActiveNav(link);
                                }
                              }}
                            >
                              <div className={`font-medium ${n.read ? 'text-zinc-600' : 'text-zinc-900'}`}>{n.title}</div>
                              {n.body && <div className="text-zinc-500 mt-0.5 line-clamp-3 whitespace-pre-line">{n.body}</div>}
                            </button>
                            <button type="button" className="text-zinc-300 hover:text-rose-500" onClick={() => void deleteNotification(n.id)}>
                              ×
                            </button>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
              <button type="button" onClick={() => setActiveNav('settings')} className="p-2 rounded-lg text-zinc-500 hover:bg-zinc-100">
                <Settings size={18} />
              </button>
              <button type="button" onClick={() => setActiveNav('profile')} className="flex items-center gap-2 pl-1">
                <AgentAvatar
                  name={displayName}
                  avatarUrl={currentAgent?.avatar_url || (user?.user_metadata?.avatar_url as string | undefined) || null}
                  size={32}
                />
                <div className="hidden md:block text-left">
                  <div className="text-xs font-medium text-zinc-800 leading-tight">{displayName}</div>
                  <div className="text-zinc-400 capitalize text-[11px]">{accountRole || 'agent'}</div>
                </div>
              </button>
              {requiresAuth && (
                <button type="button" onClick={() => { void setPresenceStatus('offline'); void signOut(); }} className="text-xs text-zinc-400 hover:text-zinc-700 px-2">
                  Sign out
                </button>
              )}
            </div>
          </header>
          <main className="flex-1 overflow-auto p-4 lg:p-6 xl:px-8 2xl:px-10 relative z-0 w-full max-w-[100vw]">
            {!usingSupabase && (
              <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 text-amber-800 text-xs px-3 py-2">
                Running offline demo data — configure Supabase for live tickets.
              </div>
            )}
            {activeNav === 'dashboard' && <Dashboard />}
            {activeNav === 'tickets' && <TicketsPage />}
            {activeNav === 'customers' && <CustomersPage />}
            {activeNav === 'team' && <TeamPage />}
            {activeNav === 'users' && (accountRole === 'admin' || !!currentAgent?.is_admin) && <UsersAdminPage />}
            {activeNav === 'users' && !(accountRole === 'admin' || currentAgent?.is_admin) && (
              <div className="text-sm text-zinc-500">Admin access required for Users.</div>
            )}
            {activeNav === 'analytics' && <AnalyticsPage />}
            {activeNav === 'knowledge' && <KnowledgePage />}
            {activeNav === 'chat' && <LiveChatPage />}
            {activeNav === 'automations' && <AutomationsPage />}
            {activeNav === 'macros' && <MacrosPage />}
            {activeNav === 'surveys' && <SurveysPage />}
            {activeNav === 'quality' && <QualityPage />}
            {activeNav === 'announcements' && <AnnouncementsPage />}
            {activeNav === 'forms' && <FormsPage />}
            {activeNav === 'releases' && <ReleasesPage />}
            {activeNav === 'settings' && <SettingsPage />}
            {activeNav === 'profile' && <ProfilePage />}
            {activeNav === 'admin-features' && admin && <AdminFeaturesPage />}
            {activeNav === 'admin-features' && !admin && (
              <div className="text-sm text-zinc-500">Admin access required.</div>
            )}
            {!TITLES[activeNav] && (
              <NotFoundScreen onGoHome={() => setActiveNav('dashboard')} />
            )}
          </main>
        </div>
      </div>
    </PostLoginShell>
  );
}

export function PortalShell() {
  const { enabled, ready } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const { user, accountRole, authBusy } = useAuth();
  const admin = accountRole === 'admin' || isAdmin;
  const [forceReady, setForceReady] = useState(false);

  // Never stick on post-login / boot screens if maintenance/auth checks hang
  useEffect(() => {
    const t = window.setTimeout(() => {
      setForceReady(true);
      try { clearJustLoggedIn(); } catch { /* ignore */ }
    }, 4500);
    return () => window.clearTimeout(t);
  }, []);

  // Customers must not wait on adminReady (agents table check) — that caused endless post-login.
  const portalBlocked =
    !forceReady &&
    (!ready ||
      !site404Ready ||
      authBusy ||
      (user && accountRole !== 'customer' && !adminReady));
  if (portalBlocked) {
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    }
    return <BootLoader label="Loading portal…" />;
  }
  if (enabled && !admin) {
    return <MaintenanceScreen />;
  }
  if (site404On && !admin) {
    return (
      <NotFoundScreen
        onGoHome={() => {
          window.location.hash = 'portal';
        }}
      />
    );
  }
  const goAgent = () => {
    window.location.hash = 'agent';
  };

  return (
    <PortalAuthGate onOpenAgent={goAgent} onBackToAgent={goAgent}>
      <CustomerPortal
        onBackToAgent={
          accountRole === 'agent' || accountRole === 'admin' || admin
            ? goAgent
            : undefined
        }
      />
    </PortalAuthGate>
  );
}

export function Root() {
  const [mode, setMode] = useState<'agent' | 'portal' | 'notfound'>(getModeFromHash);

  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  if (mode === 'notfound') {
    return (
      <NotFoundScreen
        onGoHome={() => {
          window.location.hash = '';
        }}
      />
    );
  }

  if (mode === 'portal') {
    return (
      <TicketProvider>
        <PlatformProvider>
          <PortalShell />
        </PlatformProvider>
      </TicketProvider>
    );
  }

  return (
    <TicketProvider>
      <PlatformProvider>
        <AgentShell />
      </PlatformProvider>
    </TicketProvider>
  );
}
