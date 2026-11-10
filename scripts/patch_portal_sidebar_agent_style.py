#!/usr/bin/env python3
"""Align customer portal sidebar with agent desk layout. Keeps Sign out + confirm."""
from pathlib import Path
import re

p = Path('src/components/CustomerPortal.tsx')
if not p.exists():
    print('skip CP')
    raise SystemExit(0)
s = p.read_text()

SIGNOUT_BTN = """
          <button
            type="button"
            onClick={() => {
              if (window.confirm('Sign out of the Customer Portal?')) void signOut();
            }}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-400 hover:bg-white/5 hover:text-zinc-200"
          >
            <LogOut size={16} /> Sign out
          </button>
"""


def ensure_signout(text: str) -> str:
    if re.search(r'LogOut size=\{16\} /> Sign out', text):
        return text
    matches = list(re.finditer(r'</div>\s*</aside>', text))
    if not matches:
        return text
    last = matches[-1]
    return text[: last.start()] + SIGNOUT_BTN + text[last.start() :]


def ensure_logout_import(text: str) -> str:
    if re.search(r"import\s*\{[^}]*\bLogOut\b[^}]*\}\s*from\s*'lucide-react'", text):
        return text
    return re.sub(
        r"(import\s*\{)([^}]*)(\}\s*from\s*'lucide-react')",
        lambda m: m.group(1) + m.group(2).rstrip() + ', LogOut' + m.group(3)
        if 'LogOut' not in m.group(2)
        else m.group(0),
        text,
        count=1,
    )


if 'supportNav' in s and 'openTicketBadge' in s:
    s2 = ensure_logout_import(ensure_signout(s))
    if s2 != s:
        p.write_text(s2)
        print('sidebar already agent-style; restored Sign out')
    else:
        print('sidebar already agent-style; Sign out ok')
    raise SystemExit(0)

new_nav = """
  const supportNav: { id: PortalView; label: string; icon: typeof Home }[] = [
    { id: 'home', label: 'Overview', icon: Home },
    { id: 'community', label: 'Community', icon: Users },
    { id: 'submit', label: 'Submit a Ticket', icon: Ticket },
    { id: 'chat', label: 'Live Chat', icon: MessageSquare },
    { id: 'mytickets', label: 'My Tickets', icon: ClipboardList },
    { id: 'help', label: 'Help Articles', icon: BookOpen },
  ];
  const accountNav: { id: PortalView; label: string; icon: typeof Home }[] = [
    { id: 'account', label: 'Account', icon: User },
  ];
  const navItems = [...supportNav, ...accountNav];
  const openTicketBadge = myTickets.filter((t) => {
    const st = (t.status || '').toLowerCase();
    return st && st !== 'closed' && st !== 'resolved';
  }).length;
"""

m = re.search(
    r'  const navItems: \{ id: PortalView; label: string; icon: typeof Home \}\[\] = \[[\s\S]*?\];\n',
    s,
)
if m:
    s = s[: m.start()] + new_nav + '\n' + s[m.end() :]
    print('nav ok')
elif 'supportNav' in s:
    print('nav already')
else:
    print('nav MISS')

new_aside = (
    '      <aside className="portal-sidebar hidden md:flex w-60 shrink-0 bg-zinc-950 text-zinc-100 flex flex-col h-full max-h-screen overflow-hidden relative z-30 border-r border-zinc-800/80">\n'
    '        <div className="px-4 py-5 flex items-center gap-3 border-b border-zinc-800/80">\n'
    '          <BrandMark />\n'
    '          <div className="min-w-0">\n'
    '            <div className="text-sm font-semibold tracking-tight truncate text-zinc-100">Nexus Ops</div>\n'
    '            <div className="text-[11px] text-zinc-500">Customer portal</div>\n'
    '          </div>\n'
    '        </div>\n'
    '        <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-4">\n'
    '          <div>\n'
    '            <div className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">Support</div>\n'
    '            <div className="space-y-0.5">\n'
    '              {supportNav.map((item) => {\n'
    '                const Icon = item.icon;\n'
    '                const active = view === item.id;\n'
    '                return (\n'
    '                  <button\n'
    '                    key={item.id}\n'
    '                    type="button"\n'
    '                    onClick={() => setView(item.id)}\n'
    '                    className={\n'
    "                      'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ' +\n"
    '                      (active\n'
    "                        ? 'bg-brand-600/20 text-white'\n"
    "                        : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200')\n"
    '                    }\n'
    '                  >\n'
    '                    <Icon size={18} className="shrink-0" />\n'
    '                    <span className="flex-1 text-left">{item.label}</span>\n'
    '                  </button>\n'
    '                );\n'
    '              })}\n'
    '            </div>\n'
    '          </div>\n'
    '          <div>\n'
    '            <div className="px-3 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-zinc-500">Account</div>\n'
    '            <div className="space-y-0.5">\n'
    '              {accountNav.map((item) => {\n'
    '                const Icon = item.icon;\n'
    '                const active = view === item.id;\n'
    '                return (\n'
    '                  <button\n'
    '                    key={item.id}\n'
    '                    type="button"\n'
    '                    onClick={() => setView(item.id)}\n'
    '                    className={\n'
    "                      'w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ' +\n"
    '                      (active\n'
    "                        ? 'bg-brand-600/20 text-white'\n"
    "                        : 'text-zinc-400 hover:bg-white/5 hover:text-zinc-200')\n"
    '                    }\n'
    '                  >\n'
    '                    <Icon size={18} className="shrink-0" />\n'
    '                    <span className="flex-1 text-left">{item.label}</span>\n'
    '                  </button>\n'
    '                );\n'
    '              })}\n'
    '            </div>\n'
    '          </div>\n'
    '        </nav>\n'
    '        <div className="p-3 border-t border-zinc-800/80 space-y-1">\n'
    '          {onBackToAgent && (\n'
    '            <button\n'
    '              type="button"\n'
    '              onClick={onBackToAgent}\n'
    '              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-semibold text-violet-100 bg-violet-500/20 border border-violet-400/40 hover:bg-violet-500/30"\n'
    '            >\n'
    '              <ExternalLink size={16} /> Agent Workspace\n'
    '            </button>\n'
    '          )}\n'
    '          <button\n'
    '            type="button"\n'
    "            onClick={() => setView('account')}\n"
    '            className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-white/5 transition-colors text-left"\n'
    '          >\n'
    '            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-brand-400 to-violet-500 flex items-center justify-center text-white text-xs font-semibold shrink-0">\n'
    '              {initials}\n'
    '            </div>\n'
    '            <div className="flex-1 min-w-0">\n'
    '              <div className="text-sm font-medium text-zinc-100 truncate">{displayName}</div>\n'
    '              <div className="text-[11px] text-zinc-500 truncate">{user?.email}</div>\n'
    '            </div>\n'
    '          </button>\n'
    + SIGNOUT_BTN
    + '        </div>\n'
    '      </aside>'
)

m2 = re.search(r'      <aside className="portal-sidebar[\s\S]*?</aside>', s)
if not m2:
    print('aside MISS')
else:
    s = s[: m2.start()] + new_aside + s[m2.end() :]
    print('aside ok')

s = ensure_logout_import(ensure_signout(s))
p.write_text(s)
print('done', p.stat().st_size)
