/* SystemAppCore - presence + safe login entry */
/* postlogin-agent-v1 */
import { useEffect, useRef, useState, type ReactNode } from 'react';
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
import AdminFeaturesPage from './components/AdminFeaturesPage';
import CustomerPortal from './components/CustomerPortal';
import PortalAuthGate from './components/PortalAuthGate';
import NotFoundScreen from './components/NotFoundScreen';
import { BootLoader, PostLoginShell } from './components/PostLoginLoader';
import LoginPage from './components/LoginPage';
import { TicketProvider, useTickets } from './context/TicketContext';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { useAuth } from './context/AuthContext';
import { useMaintenance } from './context/MaintenanceContext';
import { useSite404 } from './context/Site404Context';
import { publishDeskPresence, clearDeskPresence } from './lib/deskPresence';
import { useIsAdmin } from './components/useIsAdmin';
import { Bell } from 'lucide-react';
import AgentAvatar from './components/AgentAvatar';
import ThemeToggle from './components/ThemeToggle';

export function getModeFromHash(): 'agent' | 'portal' | 'notfound' {
  const h = (window.location.hash || '').replace(/^#\/?/, '').toLowerCase().split('?')[0].replace(/\/+$/, '');
  if (h === 'portal' || h.startsWith('portal/')) return 'portal';
  if (h === '404' || h === 'notfound') return 'notfound';
  return 'agent';
}

const TITLES: Record<string, string> = {
  overview: 'Overview',
  tickets: 'Tickets',
  branches: 'Branches',
  knowledge: 'Knowledge Base',
  chat: 'Live Chat',
  analytics: 'Analytics',
  team: 'Team',
  automations: 'Automations',
  macros: 'Macros',
  surveys: 'Surveys',
  quality: 'Quality',
  announcements: 'Announcements',
  forms: 'Forms',
  releases: 'Releases',
  users: 'Users',
  settings: 'Settings',
  profile: 'Profile',
  admin: 'Admin Features',
  'admin-features': 'Admin Features',
  dashboard: 'Overview',
  customers: 'Branches',
};

export function AgentShell() {
  const [activeNav, setActiveNav] = useState('overview');
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement | null>(null);
  const { currentAgent, touchPresence, setPresenceStatus } = useTickets();
  const presenceAgent = currentAgent;
  const { user, loading: authLoading, signOut } = useAuth();
  const { enabled: maintenanceOn, ready: maintenanceReady } = useMaintenance();
  const { enabled: _site404On, ready: _site404Ready } = useSite404();
  const { isAdmin } = useIsAdmin();
  const {
    notifications,
    unreadCount,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    deleteAllNotifications,
  } = usePlatform();
  const [forceReady, setForceReady] = useState(false);

  useEffect(() => {
    const t = window.setTimeout(() => setForceReady(true), 2500);
    return () => window.clearTimeout(t);
  }, []);

  useEffect(() => {
    if (!presenceAgent?.id) return;
    if ((presenceAgent.status || 'offline') === 'offline') void setPresenceStatus('online');
    void touchPresence?.();
    void publishDeskPresence({
      id: presenceAgent.id,
      name: presenceAgent.name || 'Agent',
      status: presenceAgent.status || 'online',
      avatar_url: presenceAgent.avatar_url,
      initials: presenceAgent.initials,
      color: presenceAgent.color,
      at: Date.now(),
    });
    const id = window.setInterval(() => {
      void touchPresence?.();
      void publishDeskPresence({
        id: presenceAgent.id,
        name: presenceAgent.name || 'Agent',
        status: presenceAgent.status || 'online',
        avatar_url: presenceAgent.avatar_url,
        initials: presenceAgent.initials,
        color: presenceAgent.color,
        at: Date.now(),
      });
    }, 45_000);
    const onVis = () => {
      if (document.visibilityState === 'visible') void touchPresence?.();
    };
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVis);
      void clearDeskPresence(presenceAgent.id);
    };
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  const authKnown = forceReady || !authLoading;
  if (!authKnown) {
    return <BootLoader label="Loading…" />;
  }

  if (!user) {
    return <LoginPage />;
  }

  if (maintenanceReady && maintenanceOn && !isAdmin) {
    return <BootLoader label="Maintenance" />;
  }

  const title = TITLES[activeNav] || 'Overview';

  let body: ReactNode = <Dashboard />;
  switch (activeNav) {
    case 'tickets': body = <TicketsPage />; break;
    case 'customers':
    case 'branches': body = <CustomersPage />; break;
    case 'team': body = <TeamPage />; break;
    case 'analytics': body = <AnalyticsPage />; break;
    case 'knowledge': body = <KnowledgePage />; break;
    case 'chat': body = <LiveChatPage />; break;
    case 'automations': body = <AutomationsPage />; break;
    case 'macros': body = <MacrosPage />; break;
    case 'surveys': body = <SurveysPage />; break;
    case 'quality': body = <QualityPage />; break;
    case 'announcements': body = <AnnouncementsPage />; break;
    case 'forms': body = <FormsPage />; break;
    case 'releases': body = <ReleasesPage />; break;
    case 'users': body = <UsersAdminPage />; break;
    case 'settings': body = <SettingsPage />; break;
    case 'profile': body = <ProfilePage />; break;
    case 'admin':
    case 'admin-features': body = <AdminFeaturesPage />; break;
    default: body = <Dashboard />;
  }

  return (
    <div className="flex h-screen max-h-screen overflow-hidden app-cosmos bg-zinc-50 dark:bg-transparent">
      <Sidebar
        active={activeNav}
        onNavigate={setActiveNav}
        onSignOut={() => void signOut()}
        userEmail={user?.email || ''}
        agentStatus={currentAgent?.status || 'online'}
        avatarUrl={currentAgent?.avatar_url}
        isAdmin={!!isAdmin}
      />
      <div className="flex-1 flex flex-col min-w-0 relative">
        <header className="shrink-0 h-14 px-4 flex items-center justify-between border-b border-zinc-200 bg-white/90 dark:border-zinc-800/80 dark:bg-zinc-950/80 backdrop-blur z-40">
          <h1 className="text-sm font-semibold text-zinc-800 dark:text-zinc-100">{title}</h1>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <div className="relative" ref={notifRef}>
              <button
                type="button"
                className="p-2 rounded-lg text-zinc-500 hover:text-zinc-800 hover:bg-zinc-100 dark:text-zinc-400 dark:hover:text-zinc-100 dark:hover:bg-white/5 relative"
                onClick={() => setNotifOpen((v) => !v)}
              >
                <Bell size={16} />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 w-4 h-4 text-[10px] font-bold rounded-full bg-rose-500 text-white flex items-center justify-center">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>
              {notifOpen && (
                <div className="absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto rounded-xl border border-zinc-200 bg-white dark:border-white/10 dark:bg-zinc-900 shadow-2xl z-[100]">
                  <div className="px-3 py-2 border-b border-zinc-100 dark:border-white/10 flex items-center justify-between">
                    <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">Notifications</span>
                    <button type="button" className="text-[11px] text-violet-600 dark:text-violet-300 hover:text-violet-800 dark:hover:text-white" onClick={() => void markAllNotificationsRead()}>Mark all read</button>
                  </div>
                  {(notifications || []).length === 0 ? (
                    <p className="p-4 text-xs text-zinc-500">No notifications</p>
                  ) : (
                    (notifications || []).slice(0, 30).map((n) => (
                      <button
                        key={n.id}
                        type="button"
                        className="w-full text-left px-3 py-2.5 border-b border-zinc-100 dark:border-white/5 hover:bg-zinc-50 dark:hover:bg-white/5"
                        onClick={() => {
                          void markNotificationRead(n.id);
                          setNotifOpen(false);
                        }}
                      >
                        <div className="text-xs font-medium text-zinc-800 dark:text-zinc-100 truncate">{n.title || n.body || 'Notification'}</div>
                        {n.body && <div className="text-[11px] text-zinc-500 dark:text-zinc-400 line-clamp-2 mt-0.5">{n.body}</div>}
                      </button>
                    ))
                  )}
                  {(notifications || []).length > 0 && (
                    <button type="button" className="w-full py-2 text-[11px] text-rose-600 dark:text-rose-300 hover:bg-zinc-50 dark:hover:bg-white/5" onClick={() => void deleteAllNotifications()}>Clear all</button>
                  )}
                </div>
              )}
            </div>
            {currentAgent && <AgentAvatar agent={currentAgent} size={32} />}
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6 bg-zinc-50 dark:bg-transparent">{body}</main>
      </div>
    </div>
  );
}

function PortalShell() {
  return (
    <PortalAuthGate>
      <CustomerPortal />
    </PortalAuthGate>
  );
}

/** Login without mounting full agent shell first. */
function AgentOrLogin() {
  const { user, loading: authLoading } = useAuth();
  const [forceReady, setForceReady] = useState(false);
  useEffect(() => {
    const t = window.setTimeout(() => setForceReady(true), 2500);
    return () => window.clearTimeout(t);
  }, []);
  if (!(forceReady || !authLoading)) {
    return <BootLoader label="Loading…" />;
  }
  if (!user) {
    return <LoginPage />;
  }
  return (
    <PostLoginShell ready={!!user} label="Opening agent workspace…" variant="agent">
      <AgentShell />
    </PostLoginShell>
  );
}

export function Root() {
  const [mode, setMode] = useState(() => getModeFromHash());
  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const goLogin = () => {
    try {
      localStorage.setItem('nexus-site-404-on', '0');
      localStorage.removeItem('nexus-site-404-on');
    } catch { /* ignore */ }
    window.location.hash = '';
    window.location.reload();
  };

  return (
    <TicketProvider>
      <PlatformProvider>
        {mode === 'portal' ? (
          <PortalShell />
        ) : mode === 'notfound' ? (
          <NotFoundScreen onGoHome={goLogin} onAdminSignIn={goLogin} />
        ) : (
          <AgentOrLogin />
        )}
      </PlatformProvider>
    </TicketProvider>
  );
}

export default Root;
