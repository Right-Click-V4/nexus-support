#!/usr/bin/env python3
"""Bigger titles + descriptions; agent dark chrome closer to Customer Portal."""
from pathlib import Path

p = Path("src/SystemApp.tsx")
c = p.read_text()
if "agent-chrome-meta-v1" not in c:
    old_titles = """const TITLES: Record<string, string> = {
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
};"""

    new_titles = """const TITLES: Record<string, string> = {
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

const VIEW_META: Record<string, { title: string; description: string }> = {
  dashboard: { title: 'Overview', description: 'Workspace snapshot — open work, breaches, and quick actions.' },
  tickets: { title: 'Tickets', description: 'Triage, assign, and resolve support tickets from every channel.' },
  customers: { title: 'Branches', description: 'Branch locations and related customer context.' },
  team: { title: 'Team', description: 'Agents on the desk — presence, roles, and coverage.' },
  users: { title: 'Users & access', description: 'Accounts, roles, and who can sign in to the workspace.' },
  analytics: { title: 'Analytics', description: 'Volume, SLA, and performance trends across tickets.' },
  knowledge: { title: 'Knowledge Base', description: 'Articles and answers agents use while helping customers.' },
  chat: { title: 'Live Chat', description: 'Real-time conversations with customers who need help now.' },
  automations: { title: 'Automations', description: 'Rules that route, tag, or escalate work without manual steps.' },
  macros: { title: 'Macros', description: 'Reusable replies and actions for common ticket updates.' },
  surveys: { title: 'Surveys', description: 'Collect feedback after tickets close.' },
  quality: { title: 'Quality', description: 'Review conversations and coaching signals.' },
  announcements: { title: 'Announcements', description: 'Publish marquee and portal messages for customers.' },
  forms: { title: 'Forms', description: 'Structured intake forms tied to ticket workflows.' },
  releases: { title: 'Releases', description: 'Product and ops release notes shared with the team.' },
  settings: { title: 'Settings', description: 'Workspace preferences, channels, and configuration.' },
  profile: { title: 'Profile', description: 'Your agent profile, avatar, and personal preferences.' },
  'admin-features': { title: 'Admin features', description: 'Admin-only tools for platform control and maintenance.' },
};"""

    if old_titles in c:
        c = c.replace(old_titles, new_titles, 1)
        print("VIEW_META ok")
    else:
        print("titles miss")

    old_left = """            <div className="text-sm font-semibold text-zinc-800 dark:text-zinc-100 shrink-0 min-w-0 truncate max-w-[40%]">
              {TITLES[activeNav] || activeNav}
            </div>"""
    new_left = """            <div className="shrink-0 min-w-0 max-w-[min(28rem,50%)] pr-3">
              <div className="text-lg sm:text-xl font-bold tracking-tight text-zinc-900 dark:text-white leading-tight truncate">
                {(VIEW_META[activeNav] || { title: TITLES[activeNav] || activeNav }).title}
              </div>
              <p className="text-[11px] sm:text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5 line-clamp-2">
                {(VIEW_META[activeNav] || { description: '' }).description}
              </p>
            </div>"""
    if old_left in c:
        c = c.replace(old_left, new_left, 1)
        print("title block ok")
    else:
        old2 = """            <div className="text-sm font-semibold text-zinc-800">{TITLES[activeNav] || activeNav}</div>"""
        if old2 in c:
            c = c.replace(old2, new_left, 1)
            print("title block fallback")
        else:
            print("title block miss")

    c = c.replace(
        'header className="nexus-topbar relative z-40 h-14 shrink-0 flex items-center gap-3 px-4 lg:px-6 xl:px-8 w-full"',
        'header className="nexus-topbar relative z-40 min-h-[3.75rem] h-auto py-2.5 shrink-0 flex items-center gap-3 px-4 lg:px-6 xl:px-8 w-full"',
        1,
    )

    c = "/* agent-chrome-meta-v1 */\n" + c
    p.write_text(c)
    print("sys done")
else:
    print("sys already")

css = Path("src/index.css")
s = css.read_text() if css.exists() else ""
if "agent-chrome-dark-v1" not in s:
    block = r"""
/* agent-chrome-dark-v1 — Agent Workspace dark mode closer to Customer Portal */
html.nexus-dark .app-cosmos {
  background:
    radial-gradient(ellipse 80% 50% at 20% -10%, rgba(124, 58, 237, 0.28), transparent 55%),
    radial-gradient(ellipse 60% 40% at 90% 10%, rgba(91, 33, 182, 0.22), transparent 50%),
    linear-gradient(165deg, #0a0618 0%, #12081f 40%, #0c0714 100%) !important;
  color: #e4e4e7;
}
html.nexus-dark .app-cosmos aside,
html.nexus-dark .app-cosmos aside.portal-sidebar,
html.nexus-dark aside.portal-sidebar {
  background: linear-gradient(
    180deg,
    rgba(24, 16, 48, 0.92) 0%,
    rgba(16, 10, 36, 0.94) 50%,
    rgba(12, 8, 28, 0.96) 100%
  ) !important;
  border-right: 1px solid rgba(167, 139, 250, 0.28) !important;
  box-shadow: 1px 0 24px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
html.nexus-dark .app-cosmos .nexus-topbar,
html.nexus-dark .nexus-topbar {
  background: linear-gradient(
    105deg,
    rgba(28, 18, 55, 0.9) 0%,
    rgba(20, 12, 42, 0.88) 45%,
    rgba(24, 14, 48, 0.9) 100%
  ) !important;
  border-bottom: 1px solid rgba(167, 139, 250, 0.32) !important;
  box-shadow: 0 1px 0 rgba(139, 92, 246, 0.12), 0 8px 28px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
html.nexus-dark .app-cosmos main {
  color: #e4e4e7;
}
html.nexus-dark .app-cosmos .tickets-table-panel,
html.nexus-dark .app-cosmos [class*="rounded-xl"][class*="border"][class*="shadow"],
html.nexus-dark .app-cosmos .bg-white {
  background: rgba(18, 12, 36, 0.72) !important;
  border-color: rgba(167, 139, 250, 0.22) !important;
  color: #e4e4e7;
}
html.nexus-dark .app-cosmos .tickets-table-head {
  background: rgba(30, 20, 55, 0.85) !important;
  color: #c4b5fd;
}
html.nexus-dark .app-cosmos input,
html.nexus-dark .app-cosmos select,
html.nexus-dark .app-cosmos textarea {
  background: rgba(12, 8, 28, 0.85) !important;
  border-color: rgba(255, 255, 255, 0.12) !important;
  color: #f4f4f5 !important;
}
html.nexus-dark .app-cosmos input::placeholder,
html.nexus-dark .app-cosmos textarea::placeholder {
  color: #71717a !important;
}
html.nexus-dark .app-cosmos button.border {
  border-color: rgba(255, 255, 255, 0.14);
}
html.nexus-dark .app-cosmos .text-zinc-800,
html.nexus-dark .app-cosmos .text-slate-900,
html.nexus-dark .app-cosmos .text-slate-800 {
  color: #f4f4f5 !important;
}
html.nexus-dark .app-cosmos .text-zinc-500,
html.nexus-dark .app-cosmos .text-slate-500,
html.nexus-dark .app-cosmos .text-slate-600 {
  color: #a1a1aa !important;
}
html.nexus-dark .app-cosmos aside button {
  color: #c4b5fd;
}
html.nexus-dark .app-cosmos aside button:hover {
  background: rgba(139, 92, 246, 0.15) !important;
  color: #ede9fe !important;
}
html.nexus-dark .app-cosmos aside button.bg-brand-600\/20,
html.nexus-dark .app-cosmos aside button[class*="bg-brand"] {
  background: rgba(124, 58, 237, 0.28) !important;
  color: #fff !important;
  box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.35);
}
"""
    css.write_text(s + "\n" + block)
    print("css done")
else:
    print("css already")
print("done")
