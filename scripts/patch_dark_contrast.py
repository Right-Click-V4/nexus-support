"""Fix hard-to-read Off/On controls and dark-mode text contrast."""
from pathlib import Path

af = Path('src/components/AdminFeaturesPage.tsx')
if af.exists():
    s = af.read_text()
    if 'DARK_CONTRAST_OFF_V1' in s:
        print('AdminFeatures already')
    else:
        s = s.replace(
            "maintOn ? 'bg-amber-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'",
            "maintOn ? 'bg-amber-500 text-white' : 'bg-zinc-200 text-zinc-900 hover:bg-zinc-300 dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600' /* DARK_CONTRAST_OFF_V1 */",
            1,
        )
        s = s.replace(
            "site404On ? 'bg-rose-500 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'",
            "site404On ? 'bg-rose-500 text-white' : 'bg-zinc-200 text-zinc-900 hover:bg-zinc-300 dark:bg-zinc-700 dark:text-zinc-100 dark:hover:bg-zinc-600'",
            1,
        )
        s = s.replace(
            'className="text-lg font-semibold text-slate-900"',
            'className="text-lg font-semibold text-slate-900 dark:text-zinc-50"',
            1,
        )
        s = s.replace(
            'className="text-sm text-slate-500 mt-1"',
            'className="text-sm text-slate-500 dark:text-zinc-400 mt-1"',
        )
        s = s.replace(
            'className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 flex items-center justify-between gap-4"',
            'className="bg-white dark:bg-zinc-900/80 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm p-6 flex items-center justify-between gap-4"',
        )
        s = s.replace(
            'className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-3"',
            'className="bg-white dark:bg-zinc-900/80 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm p-6 space-y-3"',
        )
        s = s.replace(
            'className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-4"',
            'className="bg-white dark:bg-zinc-900/80 rounded-xl border border-slate-200 dark:border-white/10 shadow-sm p-6 space-y-4"',
        )
        s = s.replace(
            'className="text-sm font-semibold text-slate-900"',
            'className="text-sm font-semibold text-slate-900 dark:text-zinc-50"',
        )
        af.write_text(s)
        print('AdminFeatures patched')
else:
    print('AdminFeatures missing')

an = Path('src/components/AnnouncementsPage.tsx')
if an.exists():
    s = an.read_text()
    if 'DARK_CONTRAST_OFF_V1' in s:
        print('Announcements already')
    else:
        if "{a.active === false ? 'Off' : 'Active'}" in s:
            s = s.replace(
                "{a.active === false ? 'Off' : 'Active'}",
                "{a.active === false ? 'Off' : 'Active'} /* DARK_CONTRAST_OFF_V1 */",
                1,
            )
            s = s.replace(
                "bg-zinc-100 text-zinc-600",
                "bg-zinc-100 text-zinc-800 dark:bg-zinc-700 dark:text-zinc-100",
            )
            s = s.replace(
                "bg-violet-50 text-violet-700",
                "bg-violet-50 text-violet-800 dark:bg-violet-500/20 dark:text-violet-200",
            )
            an.write_text(s)
            print('Announcements patched')
        else:
            print('Announcements Off pattern missing')
else:
    print('Announcements missing')

au = Path('src/components/AutomationsPage.tsx')
if au.exists():
    s = au.read_text()
    if "bg-slate-200'" in s or 'bg-slate-200"' in s:
        s = s.replace(
            "${a.enabled ? 'bg-emerald-500' : 'bg-slate-200'}",
            "${a.enabled ? 'bg-emerald-500' : 'bg-zinc-300 dark:bg-zinc-600'}",
        )
        au.write_text(s)
        print('Automations toggle patched')
    else:
        print('Automations skip')

st = Path('src/components/SettingsPage.tsx')
if st.exists():
    s = st.read_text()
    changed = False
    if "bg-slate-200'" in s:
        s = s.replace(
            "${dark ? 'bg-brand-600' : 'bg-slate-200'}",
            "${dark ? 'bg-brand-600' : 'bg-zinc-300 dark:bg-zinc-600'}",
        )
        s = s.replace(
            "${compact ? 'bg-brand-600' : 'bg-slate-200'}",
            "${compact ? 'bg-brand-600' : 'bg-zinc-300 dark:bg-zinc-600'}",
        )
        changed = True
    if changed:
        st.write_text(s)
        print('Settings toggles patched')
    else:
        print('Settings skip')

tm = Path('src/theme-modes.css')
if tm.exists():
    css = tm.read_text()
    if 'DARK_READABLE_OFF_V1' in css:
        print('css already')
    else:
        css = css.rstrip() + '''

/* DARK_READABLE_OFF_V1 — secondary On/Off chips stay readable on dark */
html.nexus-dark .app-cosmos button.bg-slate-100,
html.nexus-dark .app-cosmos .bg-slate-100 {
  background: #3f3f46 !important;
  color: #f4f4f5 !important;
  border-color: rgba(255, 255, 255, 0.12) !important;
  box-shadow: none !important;
}
html.nexus-dark .app-cosmos button.bg-slate-100:hover,
html.nexus-dark .app-cosmos .bg-slate-100:hover,
html.nexus-dark .app-cosmos button.hover\\:bg-slate-200:hover {
  background: #52525b !important;
  color: #fafafa !important;
}
html.nexus-dark .app-cosmos .text-slate-700,
html.nexus-dark .app-cosmos .text-slate-600 {
  color: #d4d4d8 !important;
}
html.nexus-dark .app-cosmos .text-slate-500,
html.nexus-dark .app-cosmos .text-slate-400 {
  color: #a1a1aa !important;
}
html.nexus-dark .app-cosmos .text-slate-900,
html.nexus-dark .app-cosmos .text-slate-800 {
  color: #fafafa !important;
}
html.nexus-dark .app-cosmos .bg-zinc-100 {
  background: #3f3f46 !important;
  color: #f4f4f5 !important;
}
html.nexus-dark .app-cosmos .text-zinc-600 {
  color: #d4d4d8 !important;
}
html.nexus-dark .app-cosmos .text-zinc-500 {
  color: #a1a1aa !important;
}
html.nexus-dark .app-cosmos input:not([type="checkbox"]):not([type="radio"]):not([type="range"]):not([type="color"]),
html.nexus-dark .app-cosmos textarea,
html.nexus-dark .app-cosmos select {
  background: #18181b !important;
  border-color: #3f3f46 !important;
  color: #f4f4f5 !important;
}
html.nexus-dark .app-cosmos input::placeholder,
html.nexus-dark .app-cosmos textarea::placeholder {
  color: #71717a !important;
}
'''
        tm.write_text(css)
        print('dark readable css added')
else:
    print('theme-modes missing')

print('DONE')
