#!/usr/bin/env python3
"""Stronger nav icons, sidebar dividers, lighter Overview cards, Sign out in topbar."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()

c = c.replace("iconColor: 'text-violet-500'", "iconColor: 'text-violet-700 dark:text-violet-300'")
c = c.replace("iconColor: 'text-amber-500'", "iconColor: 'text-amber-600 dark:text-amber-400'")
c = c.replace("iconColor: 'text-emerald-500'", "iconColor: 'text-emerald-600 dark:text-emerald-400'")
c = c.replace("iconColor: 'text-indigo-500'", "iconColor: 'text-indigo-700 dark:text-indigo-300'")
c = c.replace("iconColor: 'text-fuchsia-500'", "iconColor: 'text-fuchsia-600 dark:text-fuchsia-400'")
c = c.replace("iconColor: 'text-pink-500'", "iconColor: 'text-pink-600 dark:text-pink-400'")
c = c.replace("iconColor: 'text-blue-500'", "iconColor: 'text-blue-600 dark:text-blue-400'")
c = c.replace("iconColor: 'text-sky-500'", "iconColor: 'text-sky-600 dark:text-sky-400'")

old_icons = (
    'home: "text-violet-400", community: "text-sky-400", submit: "text-amber-400", '
    'chat: "text-fuchsia-400", track: "text-emerald-400", mytickets: "text-blue-400", '
    'help: "text-indigo-400", account: "text-pink-400"'
)
new_icons = (
    'home: "text-violet-700 dark:text-violet-300", community: "text-sky-600 dark:text-sky-400", '
    'submit: "text-amber-600 dark:text-amber-400", chat: "text-fuchsia-600 dark:text-fuchsia-400", '
    'track: "text-emerald-600 dark:text-emerald-400", mytickets: "text-blue-600 dark:text-blue-400", '
    'help: "text-indigo-700 dark:text-indigo-300", account: "text-pink-600 dark:text-pink-400"'
)
if old_icons in c:
    c = c.replace(old_icons, new_icons, 1)
    print("sidebar icons ok")
else:
    t2, n = re.subn(
        r'home: "text-violet-\d+", community: "text-sky-\d+", submit: "text-amber-\d+", chat: "text-fuchsia-\d+", track: "text-emerald-\d+", mytickets: "text-blue-\d+", help: "text-indigo-\d+", account: "text-pink-\d+"',
        new_icons,
        c,
        count=1,
    )
    if n:
        c = t2
        print("sidebar icons loose ok")
    else:
        print("sidebar icons miss")

old_so = """          {requiresAuth && (
            <button type="button" onClick={() => void signOut()} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-500 hover:bg-white/5 hover:text-zinc-200">
              <LogOut size={16} /> Sign out
            </button>
          )}
        </div>
      </aside>"""
new_so = """        </div>
      </aside>"""
if old_so in c:
    c = c.replace(old_so, new_so, 1)
    print("removed sidebar signout")
else:
    t2, n = re.subn(
        r'\s*\{requiresAuth && \(\s*<button type="button" onClick=\{\(\) => void signOut\(\)\} className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-zinc-500 hover:bg-white/5 hover:text-zinc-200">\s*<LogOut size=\{16\} /> Sign out\s*</button>\s*\)\}',
        "",
        c,
        count=1,
    )
    if n:
        c = t2
        print("removed sidebar signout regex")
    else:
        print("sidebar signout miss")

old_tb = """          <ThemeToggle />
        </header>"""
new_tb = """          {requiresAuth && (
            <button
              type="button"
              onClick={() => void signOut()}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-violet-500/15 dark:hover:bg-white/10 border border-violet-700/25 dark:border-white/20 transition-colors"
              title="Sign out"
            >
              <LogOut size={15} strokeWidth={2.25} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          )}
          <ThemeToggle />
        </header>"""
if old_tb in c:
    c = c.replace(old_tb, new_tb, 1)
    print("topbar signout ok")
else:
    print("topbar signout miss")

if "nav-signout-v1" not in c:
    c = c.replace("/* chrome-footer-v2 */", "/* chrome-footer-v2 */ /* nav-signout-v1 */", 1)
    if "nav-signout-v1" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* nav-signout-v1 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("cp done")

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    css = path.read_text()
    if "nav-signout-v1" in css:
        print(f"{path.name}: already")
        continue

    css = css.replace(
        ".portal-sidebar-header {\n  border-bottom: 1px solid rgba(139, 92, 246, 0.2);\n}",
        ".portal-sidebar-header {\n  border-bottom: 1px solid rgba(76, 29, 149, 0.45);\n}",
    )
    css = css.replace(
        ".portal-sidebar-footer {\n  border-top: 1px solid rgba(139, 92, 246, 0.2);\n}",
        ".portal-sidebar-footer {\n  border-top: 1px solid rgba(76, 29, 149, 0.45);\n}",
    )

    css += """

/* nav-signout-v1 — stronger icons/dividers + lighter overview cards */
html.nexus-light .portal-sidebar-header,
html.nexus-light .portal-sidebar-footer {
  border-color: rgba(76, 29, 149, 0.5) !important;
}
html.nexus-dark .portal-sidebar-header,
html.nexus-dark .portal-sidebar-footer {
  border-color: rgba(255, 255, 255, 0.28) !important;
}
html.nexus-light .portal-nav-item svg,
html.nexus-light .portal-nav-active svg {
  opacity: 1 !important;
  filter: saturate(1.35) contrast(1.1);
}
html.nexus-dark .portal-nav-item svg,
html.nexus-dark .portal-nav-active svg {
  opacity: 1 !important;
  filter: saturate(1.25) brightness(1.15);
}
html.nexus-light .portal-overview-glass {
  background: rgba(255, 255, 255, 0.55) !important;
  border-color: rgba(255, 255, 255, 0.65) !important;
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.05);
}
html.nexus-dark .portal-overview-glass {
  background: rgba(30, 24, 55, 0.42) !important;
  border-color: rgba(196, 181, 253, 0.22) !important;
}
html.nexus-light .portal-overview-glass .rounded-xl,
html.nexus-light .portal-overview-glass .rounded-2xl {
  background-color: rgba(255, 255, 255, 0.55);
}
"""
    path.write_text(css)
    print(f"{path.name}: css ok")

print("done")
