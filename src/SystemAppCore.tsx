/* SystemAppCore - restored shell with throttled presence */
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
import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './components/PostLoginLoader';
import AdminFeaturesPage from './components/AdminFeaturesPage';
import MaintenanceScreen from './components/MaintenanceScreen';
import NotFoundScreen from './components/NotFoundScreen';
import { TicketProvider, useTickets } from './context/TicketContext';
import { publishDeskPresence, clearDeskPresence } from './lib/deskPresence';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { useAuth } from './context/AuthContext';
import { useMaintenance } from './context/MaintenanceContext';
import { useSite404 } from './context/Site404Context';
import { useIsAdmin } from './components/useIsAdmin';
import { Bell, Settings, ExternalLink } from 'lucide-react';
import AgentAvatar from './components/AgentAvatar';
import ThemeToggle from './components/ThemeToggle';

export function getModeFromHash(): 'agent' | 'portal' | 'notfound' {
  const h = (window.location.hash || '').replace(/^#\/?/, '').toLowerCase().split('?')[0].replace(/\/+$/, '');
  if (h === '404' || h === 'not-found' || h === 'notfound' || h === '/') return 'notfound';
  if (h.startsWith('portal')) return 'portal';
  if (!h || h === 'agent' || h === 'app' || h === 'desk') return 'agent';
  return 'notfound';
}

const TITLES: Record<string, string> = {
  dashboard: 'Overview', tickets: 'Tickets', customers: 'Branches', team: 'Team', users: 'Users & access',
  analytics: 'Analytics', knowledge: 'Knowledge Base', chat: 'Live Chat', automations: 'Automations',
  macros: 'Macros', surveys: 'Surveys', quality: 'Quality', announcements: 'Announcements',
  forms: 'Forms', releases: 'Releases', settings: 'Settings', profile: 'Profile', 'admin-features': 'Admin features',
};

export function AgentShell() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const { tickets, currentAgent, updateAgentStatus: setPresenceStatus, touchPresence } = useTickets();
  const presenceAgent = currentAgent;
  const { user, loading: authLoading, authBusy, requiresAuth, signOut, accountRole } = useAuth();
  const { enabled: maintenanceOn, ready: maintenanceReady } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const [adminLogin, setAdminLogin] = useState(false);
  const { notifications, unreadCount, markNotificationRead, markAllNotificationsRead, deleteNotification, deleteAllNotifications, conversations } = usePlatform();

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
    });
  }, [presenceAgent?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!presenceAgent?.id) return;
    const tick = () => {
      void touchPresence?.();
      void publishDeskPresence({
        id: presenceAgent.id,
        name: presenceAgent.name || 'Agent',
        status: (presenceAgent.status || 'online') === 'offline' ? 'online' : (presenceAgent.status || 'online'),
        avatar_url: presenceAgent.avatar_url,
        initials: presenceAgent.initials,
        color: presenceAgent.color,
      });
    };
    tick();
    const id = window.setInterval(() => {
      if (typeof document !== 'undefined' && document.hidden) return;
      tick();
    }, 30_000);
    const onVis = () => { if (!document.hidden) tick(); };
    document.addEventListener('visibilitychange', onVis);
    return () => {
      window.clearInterval(id);
      document.removeEventListener('visibilitychange', onVis);
      void clearDeskPresence(presenceAgent.id);
    };
  }, [presenceAgent?.id, presenceAgent?.status, presenceAgent?.name, touchPresence]);

  useEffect(() => {
    const onDoc = (e: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(e.target as Node)) setNotifOpen(false);
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, []);

  if (requiresAuth && authLoading && !authBusy) return <BootLoader label="Loading workspace…" />;
  if (!maintenanceReady || !site404Ready) return <BootLoader label="Loading…" />;

  const admin = accountRole === 'admin' || isAdmin || !!currentAgent?.is_admin;

  if (maintenanceOn && !admin) {
    if (adminLogin || authBusy) {
      return <LoginPage audience="agent" onOpenPortal={() => { window.location.hash = 'portal'; }} />;
    }
    if (user && !adminReady) return <BootLoader label="Checking access…" />;
    return <MaintenanceScreen onAdminSignIn={!user ? () => setAdminLogin(true) : undefined} />;
  }

  if (site404On && !admin) {
    if (adminLogin || authBusy) {
      return <LoginPage audience="agent" onOpenPortal={() => { window.location.hash = 'portal'; }} />;
    }
    if (user && !adminReady) return <BootLoader label="Checking access…" />;
    return <NotFoundScreen onAdminSignIn={!user ? () => setAdminLogin(true) : undefined} onGoHome={() => { window.location.hash = ''; }} />;
  }

  if (requiresAuth && (!user || authBusy)) {
    return <LoginPage audience="customer" onOpenPortal={() => { window.location.hash = 'portal'; }} />;
  }

  if (requiresAuth && user && accountRole === 'customer' && !authBusy) {
    if (!window.location.hash.toLowerCase().includes('portal')) window.location.hash = 'portal';
    if (hasJustLoggedIn()) return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
    return <BootLoader label="Opening customer portal…" />;
  }

  const agentReady = !requiresAuth || (!!user && accountRole !== 'customer' && !authLoading && !authBusy);
  const openCount = tickets.filter((t) => !t.deleted_at && (t.status === 'new' || (t.tags || []).includes('unread'))).length;
  const displayName = currentAgent?.name || (user?.user_metadata?.full_name as string | undefined) || user?.email?.split('@')[0] || 'Agent';

  const renderPage = () => {
    switch (activeNav) {
      case 'tickets': return <TicketsPage />;
      case 'customers': return <CustomersPage />;
      case 'team': return <TeamPage />;
      case 'users': return <UsersAdminPage />;
      case 'analytics': return <AnalyticsPage />;
      case 'knowledge': return <KnowledgePage />;
      case 'chat': return <LiveChatPage />;
      case 'automations': return <AutomationsPage />;
      case 'macros': return <MacrosPage />;
      case 'surveys': return <SurveysPage />;
      case 'quality': return <QualityPage />;
      case 'announcements': return <AnnouncementsPage />;
      case 'forms': return <FormsPage />;
      case 'releases': return <ReleasesPage />;
      case 'settings': return <SettingsPage />;
      case 'profile': return <ProfilePage />;
      case 'admin-features': return <AdminFeaturesPage />;
      default: return <Dashboard onNavigate={setActiveNav} />;
    }
  };

  return (
    <PostLoginShell ready={agentReady} label="Opening agent workspace…" variant="agent">
      <div className="flex min-h-screen bg-zinc-50 dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100">
        <Sidebar active={activeNav} onNavigate={setActiveNav} openTicketCount={openCount} />
        <div className="flex-1 flex flex-col min-w-0">
          <header className="h-14 shrink-0 border-b border-zinc-200 dark:border-white/10 flex items-center justify-between px-4 gap-3">
            <div className="min-w-0">
              <div className="text-sm font-semibold truncate">{TITLES[activeNav] || 'Nexus Ops'}</div>
            </div>
            <div className="flex items-center gap-2">
              <ThemeToggle />
              <div className="relative" ref={notifRef}>
                <button type="button" onClick={() => setNotifOpen((v) => !v)} className="relative p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10">
                  <Bell size={18} />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-violet-600 text-[10px] text-white flex items-center justify-center">{unreadCount}</span>
                  )}
                </button>
                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-80 max-h-96 overflow-auto rounded-xl border border-zinc-200 dark:border-white/10 bg-white dark:bg-zinc-900 shadow-xl z-50 p-2">
                    <div className="flex items-center justify-between px-2 py-1 mb-1">
                      <span className="text-xs font-semibold">Notifications</span>
                      <button type="button" className="text-[11px] text-violet-600" onClick={() => void markAllNotificationsRead()}>Mark all read</button>
                    </div>
                    {notifications.length === 0 && <p className="text-xs text-zinc-500 p-2">No notifications</p>}
                    {notifications.slice(0, 30).map((n) => (
                      <div key={n.id} className={`px-2 py-2 rounded-lg text-xs mb-1 ${n.read ? 'opacity-60' : 'bg-violet-500/10'}`}>
                        <div className="font-medium">{n.title}</div>
                        <div className="text-zinc-500 mt-0.5">{n.body}</div>
                        <div className="flex gap-2 mt-1">
                          {!n.read && <button type="button" onClick={() => void markNotificationRead(n.id)}>Read</button>}
                          <button type="button" onClick={() => void deleteNotification(n.id)}>Delete</button>
                        </div>
                      </div>
                    ))}
                    {notifications.length > 0 && (
                      <button type="button" className="w-full text-[11px] py-1 text-rose-500" onClick={() => void deleteAllNotifications()}>Delete all</button>
                    )}
                  </div>
                )}
              </div>
              <button type="button" onClick={() => setActiveNav('settings')} className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10">
                <Settings size={18} />
              </button>
              <button type="button" onClick={() => { window.location.hash = 'portal'; }} className="p-2 rounded-lg hover:bg-zinc-100 dark:hover:bg-white/10" title="Customer portal">
                <ExternalLink size={18} />
              </button>
              <button type="button" onClick={() => setActiveNav('profile')} className="flex items-center gap-2 pl-1">
                <AgentAvatar agent={currentAgent} size="sm" />
                <span className="text-xs font-medium hidden sm:inline truncate max-w-[8rem]">{displayName}</span>
              </button>
              <button type="button" onClick={() => void signOut()} className="text-xs px-2 py-1 rounded-lg border border-zinc-200 dark:border-white/10">Sign out</button>
            </div>
          </header>
          <main className="flex-1 overflow-auto p-4">{renderPage()}</main>
        </div>
      </div>
    </PostLoginShell>
  );
}

export function PortalShell() {
  return (
    <PortalAuthGate>
      <CustomerPortal />
    </PortalAuthGate>
  );
}

export function Root() {
  const [mode, setMode] = useState(() => getModeFromHash());
  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  if (mode === 'notfound') return <NotFoundScreen onGoHome={() => { window.location.hash = ''; }} />;
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

export default Root;
