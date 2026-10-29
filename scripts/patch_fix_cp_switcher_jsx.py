#!/usr/bin/env python3
"""Repair invalid JSX from workspace switcher insert in CustomerPortal."""
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
c = p.read_text()
broken = """          {requiresAuth && (
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
fixed = """          {onBackToAgent && (
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
          )}"""
if broken in c:
    p.write_text(c.replace(broken, fixed, 1))
    print("repaired")
else:
    print("already ok or different structure")
print("done")
