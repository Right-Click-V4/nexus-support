import {
  LayoutDashboard, Ticket, Building2, BookOpen, MessageSquare,
  BarChart3, UserCog, Zap, ClipboardList, ShieldCheck,
  Megaphone, FileText, Rocket, Settings, LogOut, User, Users, MessageSquareText, Shield,
} from 'lucide-react';
import clsx from 'clsx';
import { useBranding } from '../context/BrandingContext';
import { DEFAULT_BRANDING } from '../lib/branding';

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
        <circle cx="12" cy="12" r="3" fill="white" />
        <path d="M12 3a9 9 0 0 1 9 9" stroke="white" strokeWidth="2.2" strokeLinecap="round" opacity="0.95" />
        <path d="M12 21a9 9 0 0 1-9-9" stroke="white" strokeWidth="2.2" strokeLinecap="round" opacity="0.55" />
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

  const managementItems = [
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'team', label: 'Team', icon: UserCog },
    ...(isAdmin ? [{ id: 'users', label: 'Users', icon: Users }] : []),
    { id: 'automations', label: 'Automations', icon: Zap },
    { id: 'macros', label: 'Macros', icon: MessageSquareText },
  ];

  const toolItems = [
    { id: 'surveys', label: 'Surveys', icon: ClipboardList },
    { id: 'quality', label: 'Quality', icon: ShieldCheck },
    { id: 'announcements', label: 'Announcements', icon: Megaphone },
    { id: 'forms', label: 'Forms', icon: FileText },
    { id: 'releases', label: 'Releases', icon: Rocket },
  ];

  const renderNav = (items: typeof navItems) =>
    items.map((item) => {
      const Icon = item.icon;
      const isActive = active === item.id;
      return (
        <button
          key={item.id}
          type="button"
          onClick={() => onNavigate(item.id)}
          className={clsx(
            'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors',
            isActive ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200'
          )}
        >
          <Icon size={18} className="shrink-0" />
          <span className="flex-1 text-left">{item.label}</span>
          {'badge' in item && item.badge ? (
            <span className={clsx('text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[1.25rem] text-center text-white', (item as { badgeColor?: string }).badgeColor || 'bg-brand-500')}>
              {item.badge}
            </span>
          ) : null}
        </button>
      );
    });

  return (
    <aside className="w-60 shrink-0 bg-zinc-950 text-zinc-100 flex flex-col border-r border-zinc-800/80">
      <div className="px-4 py-5 flex items-center gap-3 border-b border-zinc-800/80">
        <BrandMark logoUrl={logoUrl} />
        <div className="min-w-0">
          <div className="text-sm font-semibold tracking-tight truncate">{appName}</div>
          <div className="text-[11px] text-zinc-500">Support desk</div>
        </div>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Workspace</div>
          <div className="space-y-0.5">{renderNav(navItems)}</div>
        </div>
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Manage</div>
          <div className="space-y-0.5">{renderNav(managementItems)}</div>
        </div>
        <div>
          <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Tools</div>
          <div className="space-y-0.5">{renderNav(toolItems)}</div>
        </div>
        {isAdmin && (
          <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Admin</div>
            <div className="space-y-0.5">
              {renderNav([{ id: 'admin-features', label: 'Admin Features', icon: Shield }])}
            </div>
          </div>
        )}
      </nav>
      <div className="p-3 border-t border-zinc-800/80 space-y-1">
        <button type="button" onClick={() => onNavigate('settings')} className={clsx('w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium', active === 'settings' ? 'bg-brand-600/20 text-white' : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200')}>
          <Settings size={16} /> Settings
        </button>
        <button type="button" onClick={() => onProfile?.() || onNavigate('profile')} className={clsx('w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left', active === 'profile' ? 'bg-white/10' : 'hover:bg-white/5')}>
          <div className="relative shrink-0">
            {avatarUrl ? (
              <img src={avatarUrl} alt="" className="w-9 h-9 rounded-full object-cover ring-1 ring-white/10" />
            ) : (
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xs font-semibold">{initials}</div>
            )}
            <span
              className={`absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full border-2 border-zinc-950 ${
                agentStatus === 'online' ? 'bg-emerald-400' : agentStatus === 'busy' ? 'bg-amber-400' : agentStatus === 'away' ? 'bg-orange-400' : 'bg-zinc-500'
              }`}
              title={agentStatus}
            />
          </div>
          <div className="flex-1 min-w-0 text-left">
            <div className="text-sm font-medium text-zinc-100 truncate">{resolvedName}</div>
            <div className="text-[11px] text-zinc-500 truncate">{userEmail}</div>
          </div>
          <User size={14} className="text-zinc-500 shrink-0" />
        </button>
        {onSignOut && (
          <button type="button" onClick={() => onSignOut()} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-500 hover:bg-white/5 hover:text-zinc-200">
            <LogOut size={16} /> Sign out
          </button>
        )}
      </div>
    </aside>
  );
}
