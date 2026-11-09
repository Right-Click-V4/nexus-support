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
import AdminFeaturesPage from './components/AdminFeaturesPage';
import CustomerPortal from './components/CustomerPortal';
import PortalAuthGate from './components/PortalAuthGate';
import NotFoundScreen from './components/NotFoundScreen';
import { BootLoader } from './components/PostLoginLoader';
import LoginPage from './components/LoginPage';
import { TicketProvider, useTickets } from './context/TicketContext';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { useAuth } from './context/AuthContext';
import { useMaintenance } from './context/MaintenanceContext';
import { useSite404 } from './context/Site404Context';
import { publishDeskPresence, clearDeskPresence } from './lib/deskPresence';
import { useIsAdmin } from './components/useIsAdmin';
import { Bell, Settings, ExternalLink } from 'lucide-react';
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
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, adminReady } = useIsAdmin();
  const { notifications, unreadCount, markNotificationRead, markAllNotificationsRead, deleteNotification, deleteAllNotifications } = usePlatform();
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

  // site404On reserved for admin feature; never auto-block login shell
  void site404On;
  void site404Ready;
  void adminReady;

  const title = TITLES[activeNav] || 'Overview';

  let body: React.ReactNode = <Dashboard />;
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
    <div className="flex h-screen max-h-screen overflow-hidden app-cosmos">
      <Sidebar
        active={activeNav}
        onNavigate={setActiveNav}
        onSignOut={() => void signOut()}
        userEmail={user?.email || ''}
        agentStatus={currentAgent?.status || 'online'}
        avatarUrl={currentAgent?.avatar_url}
        isAdmin={!!isAdmin}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <header className="shrink-0 h-14 px-4 flex items-center justify-between border-b border-zinc-800/80 bg-zinc-950/80 backdrop-blur">
          <h1 className="text-sm font-semibold text-zinc-100">{title}</h1>
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <button
              type="button"
              className="p-2 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-white/5 relative"
              onClick={() => setNotifOpen((v) => !v)}
            >
              <Bell size={16} />
              {unreadCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 text-[10px] font-bold rounded-full bg-rose-500 text-white flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
            {currentAgent && <AgentAvatar agent={currentAgent} size={32} />}
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">{body}</main>
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

export function Root() {
  const [mode, setMode] = useState(() => getModeFromHash());
  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  return (
    <TicketProvider>
      <PlatformProvider>
        {mode === 'portal' ? (
          <PortalShell />
        ) : mode === 'notfound' ? (
          <NotFoundScreen
            onGoHome={() => {
              try {
                localStorage.setItem('nexus-site-404-on', '0');
                localStorage.removeItem('nexus-site-404-on');
              } catch { /* ignore */ }
              window.location.hash = '';
              window.location.reload();
            }}
            onAdminSignIn={() => {
              try {
                localStorage.setItem('nexus-site-404-on', '0');
                localStorage.removeItem('nexus-site-404-on');
              } catch { /* ignore */ }
              window.location.hash = '';
              window.location.reload();
            }}
          />
        ) : (
          <AgentShell />
        )}
      </PlatformProvider>
    </TicketProvider>
  );
}

export default Root;
