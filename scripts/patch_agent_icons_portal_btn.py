#!/usr/bin/env python3
"""Topbar nav icons + fix Customer Portal button visibility in light mode."""
from pathlib import Path

p = Path("src/SystemApp.tsx")
c = p.read_text()
if "agent-topbar-icons-v1" in c:
    print("already")
    raise SystemExit(0)

old_imp = "import { Bell, Settings, ExternalLink } from 'lucide-react';"
new_imp = """import {
  Bell,
  Settings,
  ExternalLink,
  LayoutDashboard,
  Ticket,
  Building2,
  Users,
  UserCog,
  BarChart3,
  BookOpen,
  MessageSquare,
  Zap,
  FileText,
  ClipboardList,
  Award,
  Megaphone,
  FormInput,
  Rocket,
  User,
  Shield,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';"""
if old_imp in c:
    c = c.replace(old_imp, new_imp, 1)
    print("imports ok")
else:
    print("imports miss")

if "const NAV_ICONS" not in c:
    anchor = "  'admin-features': { title: 'Admin features', description: 'Admin-only tools for platform control and maintenance.' },\n};"
    nav = """  'admin-features': { title: 'Admin features', description: 'Admin-only tools for platform control and maintenance.' },
};

const NAV_ICONS: Record<string, LucideIcon> = {
  dashboard: LayoutDashboard,
  tickets: Ticket,
  customers: Building2,
  team: Users,
  users: UserCog,
  analytics: BarChart3,
  knowledge: BookOpen,
  chat: MessageSquare,
  automations: Zap,
  macros: FileText,
  surveys: ClipboardList,
  quality: Award,
  announcements: Megaphone,
  forms: FormInput,
  releases: Rocket,
  settings: Settings,
  profile: User,
  'admin-features': Shield,
};"""
    if anchor in c:
        c = c.replace(anchor, nav, 1)
        print("NAV_ICONS ok")
    else:
        print("NAV_ICONS miss")

old_title = """            <div className="shrink-0 min-w-0 max-w-[min(28rem,50%)] pr-3">
              <div className="text-lg sm:text-xl font-bold tracking-tight text-zinc-900 dark:text-white leading-tight truncate">
                {(VIEW_META[activeNav] || { title: TITLES[activeNav] || activeNav }).title}
              </div>
              <p className="text-[11px] sm:text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5 line-clamp-2">
                {(VIEW_META[activeNav] || { description: '' }).description}
              </p>
            </div>"""
new_title = """            <div className="shrink-0 min-w-0 max-w-[min(32rem,55%)] pr-3 flex items-start gap-3">
              {(() => {
                const Icon = NAV_ICONS[activeNav] || LayoutDashboard;
                return (
                  <div className="mt-0.5 w-10 h-10 rounded-xl bg-violet-500/15 text-violet-700 dark:bg-violet-400/20 dark:text-violet-200 flex items-center justify-center shrink-0 border border-violet-400/30">
                    <Icon size={20} strokeWidth={2.25} />
                  </div>
                );
              })()}
              <div className="min-w-0">
                <div className="text-lg sm:text-xl font-bold tracking-tight text-zinc-900 dark:text-white leading-tight truncate">
                  {(VIEW_META[activeNav] || { title: TITLES[activeNav] || activeNav }).title}
                </div>
                <p className="text-[11px] sm:text-xs text-zinc-500 dark:text-zinc-400 leading-snug mt-0.5 line-clamp-2">
                  {(VIEW_META[activeNav] || { description: '' }).description}
                </p>
              </div>
            </div>"""
if old_title in c:
    c = c.replace(old_title, new_title, 1)
    print("title icon ok")
else:
    print("title icon miss")

old_btn = """                className="inline-flex items-center gap-1.5 text-xs font-medium text-zinc-600 dark:text-zinc-300 hover:text-violet-600 dark:hover:text-violet-300 px-2.5 py-1.5 rounded-lg border border-zinc-200/80 dark:border-white/10 bg-white/50 dark:bg-white/5 hover:bg-violet-50 dark:hover:bg-violet-500/10 transition-colors"
                title="Open Customer Portal"
              >
                <ExternalLink size={14} />
                <span className="hidden sm:inline">Customer Portal</span>"""
new_btn = """                className="inline-flex items-center gap-1.5 text-xs font-semibold text-violet-800 dark:text-violet-200 px-2.5 py-1.5 rounded-lg border border-violet-400/50 dark:border-violet-400/35 bg-violet-100 dark:bg-violet-500/15 hover:bg-violet-200 dark:hover:bg-violet-500/25 shadow-sm transition-colors"
                title="Open Customer Portal"
              >
                <ExternalLink size={14} className="text-violet-700 dark:text-violet-200" />
                <span className="hidden sm:inline">Customer Portal</span>"""
if old_btn in c:
    c = c.replace(old_btn, new_btn, 1)
    print("portal btn ok")
else:
    print("portal btn miss")

c = "/* agent-topbar-icons-v1 */\n" + c
p.write_text(c)
print("done")
