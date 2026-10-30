#!/usr/bin/env python3
"""Fix CustomerPortal topbar JSX: nested { } broke the build."""
from pathlib import Path

p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()
if "fix-cp-jsx-topbar-v1" in t:
    print("already")
    raise SystemExit(0)

old = """          <ThemeToggle />
          {requiresAuth && (
                          {onBackToAgent && (
                <button
                  type="button"
                  onClick={onBackToAgent}
                  className="switch-to-agent-top inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 border border-violet-500/50 shadow-md"
                  title="Back to Agent Workspace"
                >
                  <ExternalLink size={14} />
                  <span className="hidden sm:inline">Agent Workspace</span>
                </button>
              )}
<button
              type="button"
              onClick={() => void signOut()}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-violet-500/15 dark:hover:bg-white/10 border border-violet-700/25 dark:border-white/20 transition-colors"
              title="Sign out"
            >
              <LogOut size={15} strokeWidth={2.25} />
              <span className="hidden sm:inline">Sign out</span>
            </button>
          )}"""

new = """          <ThemeToggle />
          {requiresAuth && (
            <>
              {onBackToAgent && (
                <button
                  type="button"
                  onClick={onBackToAgent}
                  className="switch-to-agent-top inline-flex items-center gap-1.5 text-xs font-bold text-white px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 border border-violet-500/50 shadow-md"
                  title="Back to Agent Workspace"
                >
                  <ExternalLink size={14} />
                  <span className="hidden sm:inline">Agent Workspace</span>
                </button>
              )}
              <button
                type="button"
                onClick={() => void signOut()}
                className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs sm:text-sm font-medium text-zinc-700 dark:text-zinc-200 hover:bg-violet-500/15 dark:hover:bg-white/10 border border-violet-700/25 dark:border-white/20 transition-colors"
                title="Sign out"
              >
                <LogOut size={15} strokeWidth={2.25} />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </>
          )}"""

if old in t:
    t = t.replace(old, new, 1)
    print("fixed")
else:
    print("miss")

t = "/* fix-cp-jsx-topbar-v1 */\n" + t
p.write_text(t)
print("done")
