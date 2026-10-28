#!/usr/bin/env python3
"""Unify Action col + guide panel with table; stronger status pills; no sticky Action."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "action-unify-v1" in c:
    print("already")
    raise SystemExit(0)

c = c.replace(
    'className="px-4 py-2.5 font-semibold text-right sticky right-0 z-[5] bg-inherit portal-mytickets-action-col">Action</th>',
    'className="px-4 py-2.5 font-semibold text-right">Action</th>',
)
c = c.replace(
    'className="px-4 py-3 text-right relative sticky right-0 z-[5] portal-mytickets-action-col"',
    'className="px-4 py-3 text-right relative"',
)
c = c.replace(
    'className="px-4 sm:px-5 py-3.5 text-right relative sticky right-0 z-[5] portal-mytickets-action-col"',
    'className="px-4 sm:px-5 py-3.5 text-right relative"',
)
c = c.replace(" portal-mytickets-action-col", "")
c = c.replace("sticky right-0 z-[5] bg-inherit", "")
c = c.replace("sticky right-0 z-[5] ", "")

old_sc = """  const statusColor: Record<string, string> = {
    new: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    open: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    pending: 'bg-orange-100 text-orange-800 dark:bg-orange-500/25 dark:text-orange-200 border border-orange-300/60 dark:border-orange-400/40',
    'on-hold': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-500/25 dark:text-yellow-100 border border-yellow-300/60 dark:border-yellow-400/40',
    resolved: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/25 dark:text-emerald-200 border border-emerald-300/60 dark:border-emerald-400/40',
    closed: 'bg-red-100 text-red-800 dark:bg-red-500/25 dark:text-red-200 border border-red-300/60 dark:border-red-400/40',
  };"""
new_sc = """  const statusColor: Record<string, string> = {
    new: 'bg-violet-500 text-white dark:bg-violet-500 dark:text-white border border-violet-600/50',
    open: 'bg-violet-500 text-white dark:bg-violet-500 dark:text-white border border-violet-600/50',
    pending: 'bg-orange-500 text-white dark:bg-orange-500 dark:text-white border border-orange-600/50',
    'on-hold': 'bg-yellow-400 text-yellow-950 dark:bg-yellow-400 dark:text-yellow-950 border border-yellow-500/60',
    resolved: 'bg-emerald-500 text-white dark:bg-emerald-500 dark:text-white border border-emerald-600/50',
    closed: 'bg-red-500 text-white dark:bg-red-500 dark:text-white border border-red-600/50',
  };"""
if old_sc in c:
    c = c.replace(old_sc, new_sc, 1)
    print("statusColor ok")
else:
    print("statusColor miss")

m = re.search(r"const statusGuide = \[(.*?)\];?", c, re.S)
if m:
    new_guide = """const statusGuide = [
                { key: 'open', label: 'Open', color: 'bg-violet-500 text-white border border-violet-600/40', meaning: 'Your ticket was received and is waiting in the queue for an agent to pick it up.' },
                { key: 'pending', label: 'Pending', color: 'bg-orange-500 text-white border border-orange-600/40', meaning: 'An agent or tech support is actively working on your ticket and following up.' },
                { key: 'on-hold', label: 'On Hold', color: 'bg-yellow-400 text-yellow-950 border border-yellow-500/50', meaning: 'Work is paused \u2014 often waiting on more details from you or a third party.' },
                { key: 'resolved', label: 'Resolved', color: 'bg-emerald-500 text-white border border-emerald-600/40', meaning: 'The issue was addressed. You can still reply if something is still wrong.' },
                { key: 'closed', label: 'Closed', color: 'bg-red-500 text-white border border-red-600/40', meaning: 'The ticket is closed (for example past SLA or fully completed). Contact support if you need it reopened.' },
              ]"""
    c = c[: m.start()] + new_guide + c[m.end() :]
    print("statusGuide ok")
else:
    print("statusGuide miss")

if "action-unify-v1" not in c:
    c = "/* action-unify-v1 */\n" + c
cp.write_text(c)
print("cp done")

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    x = path.read_text()
    if "action-unify-v1" in x and "guide matches table panel" in x:
        print(f"{path.name}: already")
        continue
    x = re.sub(
        r"/\* mytickets-wider-v1 — sticky Action column \*/.*?\.dark \.portal-mytickets-action-col \{[^}]+\}",
        "/* action-unify-v1: sticky Action styles removed */",
        x,
        count=1,
        flags=re.S,
    )
    x += """

/* action-unify-v1 — guide matches table panel; no sticky Action tint */
.portal-mytickets-guide {
  background: rgba(255, 255, 255, 0.55) !important;
  backdrop-filter: blur(12px) !important;
  -webkit-backdrop-filter: blur(12px) !important;
  border-color: rgba(148, 163, 184, 0.35) !important;
}
html.nexus-dark .portal-mytickets-guide,
.dark .portal-mytickets-guide {
  background: rgba(24, 20, 42, 0.45) !important;
  border-color: rgba(167, 139, 250, 0.2) !important;
}
.portal-mytickets-action-col {
  background: transparent !important;
  box-shadow: none !important;
}
"""
    path.write_text(x)
    print(f"{path.name}: css ok")

print("done")
