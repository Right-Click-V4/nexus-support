#!/usr/bin/env python3
"""Swap ThemeToggle and Sign out order in topbar (toggle first, then Sign out)."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()

old = """          {requiresAuth && (
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

new = """          <ThemeToggle />
          {requiresAuth && (
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
        </header>"""

if old in c:
    c = c.replace(old, new, 1)
    print("swapped")
elif "<ThemeToggle />\n          {requiresAuth" in c:
    print("already swapped")
else:
    print("miss")

if "swap-signout-v1" not in c:
    c = c.replace("/* nav-signout-v1 */", "/* nav-signout-v1 */ /* swap-signout-v1 */", 1)

cp.write_text(c)
print("done")
