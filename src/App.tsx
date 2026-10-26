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
import { PostLoginShell, BootLoader } from './components/PostLoginLoader';
import AdminFeaturesPage from './components/AdminFeaturesPage';
import MaintenanceScreen from './components/MaintenanceScreen';
import { TicketProvider, useTickets } from './context/TicketContext';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { MaintenanceProvider, useMaintenance } from './context/MaintenanceContext';
import { useIsAdmin } from './components/useIsAdmin';
import { Search, Bell, Settings, ExternalLink } from 'lucide-react';
import AgentAvatar from './components/AgentAvatar';
import ThemeToggle from './components/ThemeToggle';

function getModeFromHash(): 'agent' | 'portal' {
  const h = (window.location.hash || '').replace(/^#/, '').toLowerCase();
  if (h.startsWith('portal')) return 'portal';
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

function AgentShell() {
  const [activeNav, setActiveNav] = useState('dashboard');
  const [search, setSearch] = useState('');
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);
  const { tickets, usingSupabase, currentAgent } = useTickets();
  const { user, loading: authLoading, authBusy, requiresAuth, signOut, accountRole } = useAuth();
  const { enabled: maintenanceOn, ready: maintenanceReady } = useMaintenance();
  const { isAdmin, adminReady } = useIsAdmin();
  const [adminLogin, setAdminLogin] = useState(false);
  const {
    notifications,
    unreadCount,
    markNotificationRead,
    markAllNotificationsRead,
    deleteNotification,
    deleteAllNotifications,
    conversations,
  } = usePlatform();

  const openCount = tickets.filter((t) => t.status !== 'resolved' && !t.deleted_at).length;
  const chatBadge = conversations.filter((c) => c.status !== 'ended').length;
  const displayName =
    currentAgent?.name ||
    (user?.user_metadata?.full_name as string | undefined) ||
    user?.email?.split('@')[0] ||
    'Agent';

  useEffect(() => {
    const onHash = () => {
      /* mode handled at root */
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

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

  // Wait for the shared maintenance flag before showing login or the desk.
  if (!maintenanceReady) {
    return <BootLoader label="Loading…" />;
  }

  const admin = accountRole === 'admin' || isAdmin || !!currentAgent?.is_admin;

  // Maintenance blocks the whole site (including login) except admins.
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

  // Keep login form mounted while validating so wrong-tab / pending errors show
  if (requiresAuth && (!user || authBusy)) {
    return (
      <LoginPage
        audience="agent"
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
    return <BootLoader label="Opening customer portal…" />;
  }

  const agentReady = !requiresAuth || (!!user && accountRole !== 'customer' && !authLoading && !authBusy);

  return (
    <PostLoginShell ready={agentReady} label="Opening agent workspace…" variant="agent">
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
          <header className="nexus-topbar h-14 shrink-0 flex items-center gap-3 px-4 lg:px-6">
            <div className="text-sm font-semibold text-zinc-800">{TITLES[activeNav] || activeNav}</div>
            <div className="flex-1 max-w-xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" size={16} />
                <input
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && search.trim()) {
                      setActiveNav('tickets');
                    }
                  }}
                  placeholder="Search tickets, customers, knowledge…"
                  className="nexus-search w-full pl-9 pr-3 py-2 rounded-lg text-sm outline-none"
                />
              </div>
            </div>
            <div className="flex items-center gap-1 sm:gap-2">
              <a
                href="#portal"
                className="hidden sm:inline-flex items-center gap-1 text-xs text-zinc-500 hover:text-violet-600 px-2 py-1.5 rounded-lg hover:bg-violet-50"
                title="Customer portal"
              >
                <ExternalLink size={14} /> Portal
              </a>
              <ThemeToggle />
              <div className="relative" ref={notifRef}>
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
                  <div className="absolute right-0 top-full mt-1 w-80 max-h-96 overflow-auto rounded-xl border border-zinc-200 bg-white shadow-xl z-50">
                    <div className="flex items-center justify-between px-3 py-2 border-b border-zinc-100">
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
                            <button type="button" className="text-left flex-1" onClick={() => void markNotificationRead(n.id)}>
                              <div className="font-medium text-zinc-800">{n.title}</div>
                              {n.body && <div className="text-zinc-500 mt-0.5">{n.body}</div>}
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
                <button type="button" onClick={() => void signOut()} className="text-xs text-zinc-400 hover:text-zinc-700 px-2">
                  Sign out
                </button>
              )}
            </div>
          </header>
          <main className="flex-1 overflow-auto p-4 lg:p-6">
            {!usingSupabase && (
              <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 text-amber-800 text-xs px-3 py-2">
                Running offline demo data — configure Supabase for live tickets.
              </div>
            )}
            {activeNav === 'dashboard' && <Dashboard />}
            {activeNav === 'tickets' && <TicketsPage search={search} />}
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
          </main>
        </div>
      </div>
    </PostLoginShell>
  );
}

function PortalShell() {
  const { enabled, ready } = useMaintenance();
  const { isAdmin, adminReady } = useIsAdmin();
  const { user, accountRole, authBusy } = useAuth();
  const admin = accountRole === 'admin' || isAdmin;

  if (!ready || authBusy || (user && !adminReady)) {
    return <BootLoader label="Loading portal…" />;
  }
  if (enabled && !admin) {
    return <MaintenanceScreen />;
  }
  return (
    <PortalAuthGate
      onOpenAgent={() => {
        window.location.hash = '';
      }}
    >
      <CustomerPortal />
    </PortalAuthGate>
  );
}

function Root() {
  const [mode, setMode] = useState<'agent' | 'portal'>(getModeFromHash);

  useEffect(() => {
    const onHash = () => setMode(getModeFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

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

export default function App() {
  return (
    <AuthProvider>
      <MaintenanceProvider>
        <Root />
      </MaintenanceProvider>
    </AuthProvider>
  );
}
