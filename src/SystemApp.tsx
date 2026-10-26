import { useState, useEffect, useMemo, type ReactNode } from 'react';
import {
  LayoutDashboard,
  Ticket,
  MessageSquare,
  BookOpen,
  Settings,
  Users,
  BarChart3,
  Shield,
  Bot,
  FormInput,
  Megaphone,
  Sparkles,
  ExternalLink,
  LogOut,
} from 'lucide-react';
import { useAuth } from './context/AuthContext';
import { useTickets } from './context/TicketContext';
import { PlatformProvider, usePlatform } from './context/PlatformContext';
import { TicketProvider } from './context/TicketContext';
import { useMaintenance } from './context/MaintenanceContext';
import { useSite404 } from './context/Site404Context';
import { useIsAdmin } from './hooks/useIsAdmin';
import LoginPage from './components/LoginPage';
import CustomerPortal from './components/CustomerPortal';
import PortalAuthGate from './components/PortalAuthGate';
import MaintenanceScreen from './components/MaintenanceScreen';
import NotFoundScreen from './components/NotFoundScreen';
import PostLoginLoader, { PostLoginShell, BootLoader, hasJustLoggedIn } from './components/PostLoginLoader';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import TicketQueue from './components/TicketQueue';
import LiveChat from './components/LiveChat';
import KnowledgeBase from './components/KnowledgeBase';
import TeamPage from './components/TeamPage';
import Analytics from './components/Analytics';
import SettingsPage from './components/SettingsPage';
import AutomationsPage from './components/AutomationsPage';
import FormsPage from './components/FormsPage';
import AnnouncementsPage from './components/AnnouncementsPage';
import QualityPage from './components/QualityPage';
import AgentsPage from './components/AgentsPage';

export type AgentNav =
  | 'dashboard'
  | 'tickets'
  | 'chat'
  | 'kb'
  | 'team'
  | 'analytics'
  | 'settings'
  | 'automations'
  | 'forms'
  | 'announcements'
  | 'quality'
  | 'agents';

export function getModeFromHash(): 'agent' | 'portal' | 'notfound' {
  const h = (window.location.hash || '').replace(/^#/, '').toLowerCase().split('?')[0];
  if (h.startsWith('portal')) return 'portal';
  if (h && !h.startsWith('portal') && !['', 'agent', 'app', 'desk'].includes(h) && h.includes('/')) {
    return 'notfound';
  }
  return 'agent';
}

function AgentShell() {
  const { user, loading: authLoading, authBusy, requiresAuth, signOut, accountRole } = useAuth();
  const { tickets, openCount } = useTickets();
  const { conversations } = usePlatform();
  const [activeNav, setActiveNav] = useState<AgentNav>('dashboard');

  const chatBadge = useMemo(
    () => conversations.filter((c) => c.status === 'waiting' || (c.unread && c.unread > 0)).length,
    [conversations],
  );

  const displayName =
    (user?.user_metadata?.full_name as string) || user?.email?.split('@')[0] || 'Agent';

  const currentAgent = useMemo(() => {
    return null as { avatar_url?: string; status?: string } | null;
  }, []);

  if (authLoading && !authBusy) {
    return <BootLoader label="Loading workspace…" />;
  }

  if (requiresAuth && authBusy && !user) {
    return <BootLoader label="Loading…" />;
  }

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
    if (hasJustLoggedIn()) {
      return <PostLoginLoader label="Opening customer portal…" fading={false} variant="customer" />;
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
          onSignOut={() => void signOut()}
        />
        <main className="flex-1 min-w-0 overflow-y-auto">
          {activeNav === 'dashboard' && <Dashboard onNavigate={setActiveNav} />}
          {activeNav === 'tickets' && <TicketQueue />}
          {activeNav === 'chat' && <LiveChat />}
          {activeNav === 'kb' && <KnowledgeBase />}
          {activeNav === 'team' && <TeamPage />}
          {activeNav === 'analytics' && <Analytics />}
          {activeNav === 'settings' && <SettingsPage />}
          {activeNav === 'automations' && <AutomationsPage />}
          {activeNav === 'forms' && <FormsPage />}
          {activeNav === 'announcements' && <AnnouncementsPage />}
          {activeNav === 'quality' && <QualityPage />}
          {activeNav === 'agents' && <AgentsPage />}
        </main>
      </div>
    </PostLoginShell>
  );
}

export function PortalShell() {
  const { enabled, ready } = useMaintenance();
  const { enabled: site404On, ready: site404Ready } = useSite404();
  const { isAdmin, ready: adminReady } = useIsAdmin();
  const { user, accountRole, authBusy } = useAuth();
  const admin = accountRole === 'admin' || isAdmin;

  if (!ready || !site404Ready || authBusy || (user && !adminReady)) {
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
