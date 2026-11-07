"""Match customer portal sidebar to agent design + fix light mode mess."""
from pathlib import Path
import re

# --- 1) CustomerPortal sidebar ---
cp = Path('src/components/CustomerPortal.tsx')
if cp.exists() and cp.stat().st_size > 10000:
    s = cp.read_text()
    if 'SIDEBAR_MATCH_AGENT_V1' in s:
        print('CP sidebar already matched')
    else:
        old_aside_start = s.find('<aside className="portal-sidebar')
        if old_aside_start < 0:
            print('portal-sidebar aside not found')
        else:
            old_aside_end = s.find('</aside>', old_aside_start) + len('</aside>')
            new_aside = r'''<aside className="/* SIDEBAR_MATCH_AGENT_V1 */ w-60 shrink-0 bg-zinc-950 text-zinc-100 flex flex-col border-r border-zinc-800/80 hidden md:flex h-full max-h-screen overflow-hidden relative z-30">
        <div className="px-4 py-5 flex items-center gap-3 border-b border-zinc-800/80">
          <BrandMark />
          <div className="min-w-0">
            <div className="text-sm font-semibold tracking-tight truncate text-zinc-50">Nexus Ops</div>
            <div className="text-[11px] text-zinc-500">Customer portal</div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
          <div>
            <div className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">Support</div>
            <div className="space-y-0.5">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = view === item.id || (view === 'success' && item.id === 'submit');
                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setView(item.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      active
                        ? 'bg-brand-600/20 text-white'
                        : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200'
                    }`}
                  >
                    <Icon size={18} className="shrink-0" />
                    <span className="flex-1 text-left">{item.label}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </nav>

        <div className="p-3 border-t border-zinc-800/80 space-y-1">
          {onBackToAgent && (
            <button
              type="button"
              onClick={onBackToAgent}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-violet-300 hover:bg-violet-500/15 hover:text-violet-100"
            >
              <ExternalLink size={16} /> Agent Workspace
            </button>
          )}
          <button
            type="button"
            onClick={() => setView('account')}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left ${
              view === 'account' ? 'bg-white/10' : 'hover:bg-white/5'
            }`}
          >
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xs font-semibold shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <div className="text-sm font-medium text-zinc-100 truncate">{displayName}</div>
              <div className="text-[11px] text-zinc-500 truncate">{user?.email}</div>
            </div>
            <User size={14} className="text-zinc-500 shrink-0" />
          </button>
          <button
            type="button"
            onClick={() => void signOut()}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-rose-300/90 hover:bg-rose-500/10 hover:text-rose-200 border border-transparent hover:border-rose-500/20"
          >
            <LogOut size={16} /> Sign out
          </button>
        </div>
      </aside>'''
            s = s[:old_aside_start] + new_aside + s[old_aside_end:]
            cp.write_text(s)
            print('CP sidebar matched to agent')
else:
    print('CP missing or stub')

# --- 2) Fix light mode CSS (theme-modes.css) ---
tm = Path('src/theme-modes.css')
if tm.exists():
    css = tm.read_text()
    if 'LIGHT_MODE_SIDEBAR_FIX_V1' in css:
        print('theme-modes already fixed')
    else:
        old = '''html.nexus-light .app-cosmos .bg-white,
html.nexus-light .app-cosmos [class*="bg-white"] {
  background: #ffffff !important;
  border-color: #e4e4e7 !important;
  color: #18181b !important;
  box-shadow: 0 1px 3px rgba(24, 24, 27, 0.06), 0 4px 16px rgba(91, 33, 182, 0.04) !important;
}'''
        new = '''/* LIGHT_MODE_SIDEBAR_FIX_V1 — do not match utility fragments like hover:bg-white/5 */
html.nexus-light .app-cosmos .bg-white {
  background: #ffffff !important;
  border-color: #e4e4e7 !important;
  color: #18181b !important;
  box-shadow: 0 1px 3px rgba(24, 24, 27, 0.06), 0 4px 16px rgba(91, 33, 182, 0.04) !important;
}
html.nexus-light .app-cosmos .bg-white\\/50,
html.nexus-light .app-cosmos .bg-white\\/80,
html.nexus-light .app-cosmos .bg-white\\/90,
html.nexus-light .app-cosmos .bg-white\\/95 {
  background: rgba(255, 255, 255, 0.92) !important;
  color: #18181b !important;
}'''
        if old in css:
            css = css.replace(old, new, 1)
            print('fixed light bg-white selector')
        else:
            print('light bg-white block not found exactly')

        protect = '''

/* LIGHT_MODE_SIDEBAR_FIX_V1 — keep agent + portal sidebars solid dark in both themes */
html.nexus-light aside.portal-sidebar,
html.nexus-dark aside.portal-sidebar,
html.nexus-light .app-cosmos > aside,
html.nexus-dark .app-cosmos > aside,
html.nexus-light aside.w-60,
html.nexus-dark aside.w-60 {
  background: #09090b !important;
  color: #f4f4f5 !important;
  border-right: 1px solid rgba(39, 39, 42, 0.85) !important;
  backdrop-filter: none !important;
}
html.nexus-light aside.portal-sidebar .portal-sidebar-title,
html.nexus-light aside.portal-sidebar .text-zinc-50,
html.nexus-light .app-cosmos > aside .text-sm.font-semibold {
  color: #fafafa !important;
}
html.nexus-light aside.portal-sidebar .portal-sidebar-sub,
html.nexus-light aside.portal-sidebar .text-zinc-500,
html.nexus-light .app-cosmos > aside .text-zinc-500 {
  color: #71717a !important;
}
html.nexus-light aside.portal-sidebar .portal-sidebar-label,
html.nexus-light aside.portal-sidebar .text-zinc-600,
html.nexus-light .app-cosmos > aside .text-zinc-600 {
  color: #52525b !important;
}
html.nexus-light aside.portal-sidebar .portal-nav-item,
html.nexus-light aside.portal-sidebar button,
html.nexus-light .app-cosmos > aside button {
  color: #a1a1aa !important;
  background: transparent !important;
  box-shadow: none !important;
  border-color: transparent !important;
}
html.nexus-light aside.portal-sidebar .portal-nav-active,
html.nexus-light aside.portal-sidebar button.portal-nav-active,
html.nexus-light .app-cosmos > aside button.bg-brand-600\\/20,
html.nexus-light .app-cosmos > aside .bg-brand-600\\/20 {
  background: rgba(124, 58, 237, 0.28) !important;
  color: #ffffff !important;
}
html.nexus-light aside.portal-sidebar button:hover,
html.nexus-light .app-cosmos > aside button:hover {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #e4e4e7 !important;
}
html.nexus-light .app-cosmos > aside button.text-white {
  color: #ffffff !important;
}

html.nexus-light .portal-shell .nexus-topbar {
  background: rgba(255, 255, 255, 0.92) !important;
  border-bottom: 1px solid #e4e4e7 !important;
  color: #18181b !important;
}
html.nexus-light .portal-shell .nexus-topbar .text-zinc-900,
html.nexus-light .portal-shell .nexus-topbar .text-zinc-50 {
  color: #18181b !important;
}
html.nexus-light .portal-shell .nexus-topbar .text-zinc-500,
html.nexus-light .portal-shell .nexus-topbar .text-zinc-400 {
  color: #71717a !important;
}
'''
        css = css.rstrip() + protect
        tm.write_text(css)
        print('appended sidebar light-mode protection')
else:
    print('theme-modes.css missing')

# --- 3) Override portal-lounge purple gradient sidebar ---
pl = Path('src/portal-lounge.css')
if pl.exists():
    lounge = pl.read_text()
    if 'SIDEBAR_MATCH_AGENT_V1' in lounge:
        print('lounge already overridden')
    else:
        override = '''

/* SIDEBAR_MATCH_AGENT_V1 — force portal sidebar to match agent solid dark rail */
.portal-sidebar,
html.nexus-light .portal-sidebar,
html.nexus-dark .portal-sidebar,
html.nexus-light .app-cosmos > aside.portal-sidebar,
html.nexus-dark .app-cosmos > aside.portal-sidebar,
.app-cosmos > aside.portal-sidebar {
  background: #09090b !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
  border-right: 1px solid rgba(39, 39, 42, 0.85) !important;
  color: #f4f4f5 !important;
}
.portal-sidebar-header,
html.nexus-dark .portal-sidebar-header {
  border-bottom: 1px solid rgba(39, 39, 42, 0.85) !important;
}
.portal-sidebar-footer,
html.nexus-dark .portal-sidebar-footer {
  border-top: 1px solid rgba(39, 39, 42, 0.85) !important;
}
.portal-sidebar-title { color: #fafafa !important; }
.portal-sidebar-sub { color: #71717a !important; }
.portal-sidebar-label { color: #52525b !important; }
.portal-nav-item { color: #a1a1aa !important; }
.portal-nav-item:hover {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #e4e4e7 !important;
}
.portal-nav-active {
  background: rgba(124, 58, 237, 0.28) !important;
  color: #ffffff !important;
}
'''
        pl.write_text(lounge.rstrip() + override)
        print('lounge sidebar forced to agent dark')
else:
    print('portal-lounge.css missing')

print('done')
