"""Fix agent notif bell, restore Users nav, remove Desk online chip, portal logout blank."""
from pathlib import Path
import re

core = Path('src/SystemAppCore.tsx')
if core.exists():
    s = core.read_text()
    if 'SHELL_FIXES_V1' in s:
        print('SystemAppCore already fixed')
    else:
        if 'PortalAuthGate' not in s:
            if "import CustomerPortal from './components/CustomerPortal';" in s:
                s = s.replace(
                    "import CustomerPortal from './components/CustomerPortal';",
                    "import CustomerPortal from './components/CustomerPortal';\nimport PortalAuthGate from './components/PortalAuthGate';",
                    1,
                )
                print('imported PortalAuthGate')

        old_side = '''      <Sidebar
        active={activeNav}
        onNavigate={setActiveNav}
        onSignOut={() => void signOut()}
        userName={currentAgent?.name || user?.email || 'Agent'}
        userEmail={user?.email || ''}
        avatarUrl={currentAgent?.avatar_url}
        agentStatus={currentAgent?.status || 'online'}
      />'''
        new_side = '''      <Sidebar
        /* SHELL_FIXES_V1 */
        active={activeNav}
        onNavigate={setActiveNav}
        onSignOut={() => void signOut()}
        userName={currentAgent?.name || user?.email || 'Agent'}
        userEmail={user?.email || ''}
        avatarUrl={currentAgent?.avatar_url}
        agentStatus={currentAgent?.status || 'online'}
        isAdmin={isAdmin || !!currentAgent?.is_admin}
      />'''
        if old_side in s:
            s = s.replace(old_side, new_side, 1)
            print('Sidebar isAdmin passed')
        else:
            print('Sidebar block not exact')

        if 'notifOpen &&' not in s and 'setNotifOpen' in s:
            old_bell = '''            <div className="relative" ref={notifRef}>
              <button type="button" onClick={() => setNotifOpen((v) => !v)} className="relative p-2 rounded-lg hover:bg-white/10">
                <Bell size={16} />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center">{unreadCount > 9 ? '9+' : unreadCount}</span>
                )}
              </button>
            </div>'''
            new_bell = '''            <div className="relative" ref={notifRef}>
              <button type="button" onClick={() => setNotifOpen((v) => !v)} className="relative p-2 rounded-lg hover:bg-white/10 text-zinc-200" title="Notifications" aria-label="Notifications">
                <Bell size={16} />
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 px-1 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center">{unreadCount > 9 ? '9+' : unreadCount}</span>
                )}
              </button>
              {notifOpen && (
                <div className="absolute right-0 top-full mt-2 w-80 max-w-[min(20rem,calc(100vw-2rem))] rounded-xl border border-white/15 bg-zinc-950 shadow-2xl z-[90] overflow-hidden">
                  <div className="flex items-center justify-between px-3 py-2.5 border-b border-white/10">
                    <span className="text-sm font-semibold text-zinc-100">Notifications</span>
                    <div className="flex items-center gap-2">
                      {unreadCount > 0 && (
                        <button type="button" className="text-[11px] text-violet-300 hover:text-white" onClick={() => void markAllNotificationsRead()}>
                          Mark all read
                        </button>
                      )}
                      {notifications.length > 0 && (
                        <button type="button" className="text-[11px] text-zinc-500 hover:text-rose-300" onClick={() => void deleteAllNotifications()}>
                          Clear
                        </button>
                      )}
                    </div>
                  </div>
                  <div className="max-h-72 overflow-y-auto">
                    {notifications.length === 0 ? (
                      <p className="px-3 py-6 text-center text-xs text-zinc-500">No notifications yet</p>
                    ) : (
                      notifications.slice(0, 30).map((n) => (
                        <button
                          key={n.id}
                          type="button"
                          onClick={() => {
                            void markNotificationRead(n.id);
                            setNotifOpen(false);
                            if ((n.link || '').toLowerCase().includes('chat')) setActiveNav('chat');
                            else if ((n.link || '').toLowerCase().includes('ticket')) setActiveNav('tickets');
                          }}
                          className={`w-full text-left px-3 py-2.5 border-b border-white/5 hover:bg-white/5 ${n.read ? 'opacity-60' : ''}`}
                        >
                          <div className="text-sm font-medium text-zinc-100 truncate">{n.title}</div>
                          {n.body ? <div className="text-[11px] text-zinc-400 line-clamp-2 mt-0.5">{n.body}</div> : null}
                          <div className="text-[10px] text-zinc-500 mt-1">{n.created_at ? new Date(n.created_at).toLocaleString() : ''}</div>
                        </button>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>'''
            if old_bell in s:
                s = s.replace(old_bell, new_bell, 1)
                print('notif dropdown added')
            else:
                print('bell block not found exact')

        old_portal = '''function PortalShell() {
  return <CustomerPortal />;
}'''
        new_portal = '''function PortalShell() {
  // SHELL_FIXES_V1 — show login after customer logout (no blank screen)
  return (
    <PortalAuthGate>
      <CustomerPortal />
    </PortalAuthGate>
  );
}'''
        if old_portal in s:
            s = s.replace(old_portal, new_portal, 1)
            print('PortalAuthGate wrapped')
        else:
            print('PortalShell not found')

        core.write_text(s)
        print('SystemAppCore written')
else:
    print('SystemAppCore missing')

sb = Path('src/components/Sidebar.tsx')
if sb.exists():
    s = sb.read_text()
    if 'USERS_NAV_ALWAYS_V1' in s:
        print('Sidebar users already')
    else:
        old = "    ...(isAdmin ? [{ id: 'users', label: 'Users', icon: Users }] : []),"
        new = "    { id: 'users', label: 'Users', icon: Users }, // USERS_NAV_ALWAYS_V1"
        if old in s:
            s = s.replace(old, new, 1)
            sb.write_text(s)
            print('Users always visible')
        elif "id: 'users'" in s:
            print('users entry exists')
        else:
            if "{ id: 'team', label: 'Team', icon: UserCog }," in s:
                s = s.replace(
                    "{ id: 'team', label: 'Team', icon: UserCog },",
                    "{ id: 'team', label: 'Team', icon: UserCog },\n    { id: 'users', label: 'Users', icon: Users }, // USERS_NAV_ALWAYS_V1",
                    1,
                )
                sb.write_text(s)
                print('Users injected')
            else:
                print('could not add users')
else:
    print('Sidebar missing')

lp = Path('src/components/LoginPage.tsx')
if lp.exists():
    s = lp.read_text()
    if 'DESK_ONLINE_REMOVED_V1' in s:
        print('desk chip already removed')
    else:
        pattern = re.compile(
            r'\s*<div className="login-status-pill mb-4 inline-flex items-center gap-2">\s*'
            r'<span className="login-status-dot" />\s*'
            r'<span>Desk online</span>\s*'
            r'<span className="mx-1 text-fuchsia-300/30">·</span>\s*'
            r'<span className="text-fuchsia-200/70">Avg reply under 5 min</span>\s*'
            r'</div>',
            re.S,
        )
        if pattern.search(s):
            s = pattern.sub('\n              {/* DESK_ONLINE_REMOVED_V1 */}', s, 1)
            lp.write_text(s)
            print('desk online removed')
        elif 'Desk online' in s:
            s = s.replace('Desk online', '')
            s = s.replace('Avg reply under 5 min', '')
            lp.write_text(s)
            print('desk online text stripped')
        else:
            print('desk online not found')
else:
    print('LoginPage missing')

print('DONE')
