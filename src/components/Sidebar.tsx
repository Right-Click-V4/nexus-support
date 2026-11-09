/* signout-confirm-v1 */
/* admin-features-always-v1 */
/* status-dot-match-v1 */
import { useState } from 'react';
import {
  LayoutDashboard, Ticket, Building2, BookOpen, MessageSquare,
  BarChart3, UserCog, Zap, ClipboardList, ShieldCheck,
  Megaphone, FileText, Rocket, Settings, LogOut, User, Users, MessageSquareText, Shield,
} from 'lucide-react';
import clsx from 'clsx';
import { useBranding } from '../context/BrandingContext';
import { DEFAULT_BRANDING } from '../lib/branding';


function statusDotClass(status?: string) {
  switch ((status || 'online').toLowerCase()) {
    case 'online':
      return 'bg-emerald-400';
    case 'away':
      return 'bg-sky-400';
    case 'busy':
      return 'bg-amber-300';
    case 'in_call':
      return 'bg-orange-400';
    case 'custom':
      return 'bg-white';
    case 'offline':
      return 'bg-zinc-500';
    default:
      return 'bg-emerald-400';
  }
}

function statusLabel(status?: string) {
  switch ((status || 'online').toLowerCase()) {
    case 'online':
      return 'Available';
    case 'away':
      return 'Away';
    case 'busy':
      return 'Busy';
    case 'in_call':
      return 'In call';
    case 'custom':
      return 'Custom';
    case 'offline':
      return 'Offline';
    default:
      return status || 'Available';
  }
}

interface SidebarProps {
  active: string;
  onNavigate: (id: string) => void;
  ticketCount?: number;
  openCount?: number;
  chatCount?: number;
  chatBadge?: number;
  userName?: string;
  displayName?: string;
  userEmail?: string;
  avatarUrl?: string | null;
  agentStatus?: string;
  onSignOut?: () => void;
  onProfile?: () => void;
  isAdmin?: boolean;
}

/* labels-titlecase-v1 */
function BrandMark({ logoUrl, className = 'w-8 h-8' }: { logoUrl?: string; className?: string }) {
  if (logoUrl) {
    return (
      <div className={`${className} rounded-xl overflow-hidden bg-white/10 ring-1 ring-white/15 flex items-center justify-center shrink-0`}>
        <img src={logoUrl} alt="" className="w-full h-full object-contain" />
      </div>
    );
  }
  return (
    <div className={`${className} rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 flex items-center justify-center shadow-md shadow-brand-900/40 shrink-0`}>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M4 4 L20 20 M20 4 L4 20" stroke="white" strokeWidth="3.2" strokeLinecap="round" />
        <path d="M12 2 L13.6 9.6 L21 11.2 L13.6 12.8 L12 20.5 L10.4 12.8 L3 11.2 L10.4 9.6 Z" fill="white" />
        <circle cx="12" cy="11.2" r="1.4" fill="white" />
      </svg>
    </div>
  );
}

export default function Sidebar({
  active,
  onNavigate,
  ticketCount = 0,
  openCount,
  chatCount = 0,
  chatBadge,
  userName = 'Agent',
  displayName,
  userEmail = '',
  avatarUrl,
  agentStatus = 'online',
  onSignOut,
  onProfile,
  isAdmin = false,
}: SidebarProps) {
  const [confirmSignOut, setConfirmSignOut] = useState(false);

  const { branding } = useBranding();
  const appName = (branding.appName || '').trim() || DEFAULT_BRANDING.appName;
  const logoUrl = (branding.logoUrl || '').trim();

  const resolvedName = displayName || userName;
  const resolvedTickets = openCount ?? ticketCount;
  const resolvedChats = chatBadge ?? chatCount;
  const initials = resolvedName.split(' ').map((p) => p[0]).join('').slice(0, 2).toUpperCase() || 'AG';

  const navItems = [
    { id: 'dashboard', label: 'Overview', icon: LayoutDashboard },
    { id: 'tickets', label: 'Tickets', icon: Ticket, badge: resolvedTickets || undefined },
    { id: 'customers', label: 'Branches', icon: Building2 },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'chat', label: 'Live Chat', icon: MessageSquare, badge: resolvedChats || undefined, badgeColor: 'bg-emerald-500' },
  ];

  const manageItems = [
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'team', label: 'Team', icon: Users },
    { id: 'users', label: 'Users', icon: UserCog },
    { id: 'automations', label: 'Automations', icon: Zap },
    { id: 'macros', label: 'Macros', icon: MessageSquareText },
    { id: 'surveys', label: 'Surveys', icon: ClipboardList },
    { id: 'quality', label: 'Quality', icon: ShieldCheck },
    { id: 'announcements', label: 'Announcements', icon: Megaphone },
    { id: 'forms', label: 'Forms', icon: FileText },
    { id: 'releases', label: 'Releases', icon: Rocket },
  ];

  return (
    <aside className="w-64 shrink-0 flex flex-col bg-zinc-950 border-r border-zinc-800/80 min-h-screen">
      <div className="px-4 py-5 flex items-center gap-3 border-b border-zinc-800/80">
        <BrandMark logoUrl={logoUrl} />
        <div className="min-w-0">
          <div className="text-sm font-semibold tracking-tight truncate text-zinc-100">{appName}</div>
          <div className="text-[11px] text-zinc-500">Support desk</div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Workspace</div>
          <div className="space-y-0.5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = active === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                  className={clsx(
                    'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200',
                  )}
                >
                  <Icon size={18} className="shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                  {item.badge ? (
                    <span className={clsx('text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center text-white', item.badgeColor || 'bg-brand-500')}>
                      {item.badge}
                    </span>
                  ) : null}
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Manage</div>
          <div className="space-y-0.5">
            {manageItems.map((item) => {
              const Icon = item.icon;
              const isActive = active === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                  className={clsx(
                    'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200',
                  )}
                >
                  <Icon size={18} className="shrink-0" />
                  <span className="flex-1 text-left">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Tools</div>
          <div className="space-y-0.5">
            <button
              type="button"
              onClick={() => onNavigate('settings')}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                active === 'settings' ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200',
              )}
            >
              <Settings size={18} className="shrink-0" />
              <span className="flex-1 text-left">Settings</span>
            </button>
            {isAdmin && (
              <button
                type="button"
                onClick={() => onNavigate('admin-features')}
                className={clsx(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  active === 'admin-features' ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200',
                )}
              >
                <Shield size={18} className="shrink-0" />
                <span className="flex-1 text-left">Admin features</span>
              </button>
            )}
          </div>
        </div>
      </nav>

      <div className="p-3 border-t border-zinc-800/80 space-y-2">
        <button type="button" onClick={() => onProfile?.() || onNavigate('profile')} className={clsx('w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left', active === 'profile' ? 'bg-white/10' : 'hover:bg-white/5')}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-[10px] font-bold text-white overflow-hidden shrink-0">
            {avatarUrl ? <img src={avatarUrl} alt="" className="w-full h-full object-cover" /> : initials}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-medium text-zinc-100 truncate">{resolvedName}</div>
            <div className="text-[10px] text-zinc-500 truncate flex items-center gap-1">
              <span className={clsx('inline-block w-1.5 h-1.5 rounded-full', statusDotClass(agentStatus))} />
              <span className="truncate">{statusLabel(agentStatus)}</span>
            </div>
          </div>
        </button>
        <button
          type="button"
          onClick={() => setConfirmSignOut(true)}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
        >
          <LogOut size={16} /> Sign out
        </button>
      </div>

      {confirmSignOut && (
        <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-2xl border border-white/15 bg-zinc-900 shadow-2xl p-5 space-y-4">
            <h2 className="text-base font-semibold text-zinc-50">Sign out?</h2>
            <p className="text-sm text-zinc-400">You will need to sign in again to access the agent workspace.</p>
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setConfirmSignOut(false)} className="px-3.5 py-2 rounded-xl text-sm border border-white/15 text-zinc-200 hover:bg-white/5">Cancel</button>
              <button type="button" onClick={() => { setConfirmSignOut(false); if (onSignOut) onSignOut(); else window.location.hash = ''; }} className="px-3.5 py-2 rounded-xl text-sm font-semibold text-white bg-rose-600 hover:bg-rose-500">Sign out</button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
