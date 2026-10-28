#!/usr/bin/env python3
"""Align status colors with agent workspace; drop New; tighten table height."""
from pathlib import Path
import re

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()
if "status-colors-space-v1" in c:
    print("already")
    raise SystemExit(0)

old_sc = """  const statusColor: Record<string, string> = {
    new: 'bg-violet-100 text-violet-700',
    open: 'bg-amber-100 text-amber-700',
    pending: 'bg-violet-100 text-violet-700',
    'on-hold': 'bg-zinc-100 text-zinc-600',
    resolved: 'bg-emerald-100 text-emerald-700',
  };"""
new_sc = """  const statusColor: Record<string, string> = {
    new: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    open: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/60 dark:border-violet-400/40',
    pending: 'bg-orange-100 text-orange-800 dark:bg-orange-500/25 dark:text-orange-200 border border-orange-300/60 dark:border-orange-400/40',
    'on-hold': 'bg-yellow-100 text-yellow-900 dark:bg-yellow-500/25 dark:text-yellow-100 border border-yellow-300/60 dark:border-yellow-400/40',
    resolved: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/25 dark:text-emerald-200 border border-emerald-300/60 dark:border-emerald-400/40',
    closed: 'bg-red-100 text-red-800 dark:bg-red-500/25 dark:text-red-200 border border-red-300/60 dark:border-red-400/40',
  };"""
if old_sc in c:
    c = c.replace(old_sc, new_sc, 1)
    print("statusColor ok")
else:
    print("statusColor miss")

m = re.search(r"const statusGuide = \[(.*?)\];", c, re.S)
if m:
    new_guide = """const statusGuide = [
                { key: 'open', label: 'Open', color: 'bg-violet-100 text-violet-800 dark:bg-violet-500/25 dark:text-violet-200 border border-violet-300/50 dark:border-violet-400/40', meaning: 'Your ticket was received and is waiting in the queue for an agent to pick it up.' },
                { key: 'pending', label: 'Pending', color: 'bg-orange-100 text-orange-800 dark:bg-orange-500/25 dark:text-orange-200 border border-orange-300/50 dark:border-orange-400/40', meaning: 'An agent or tech support is actively working on your ticket and following up.' },
                { key: 'on-hold', label: 'On Hold', color: 'bg-yellow-100 text-yellow-900 dark:bg-yellow-500/25 dark:text-yellow-100 border border-yellow-300/50 dark:border-yellow-400/40', meaning: 'Work is paused \u2014 often waiting on more details from you or a third party.' },
                { key: 'resolved', label: 'Resolved', color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-500/25 dark:text-emerald-200 border border-emerald-300/50 dark:border-emerald-400/40', meaning: 'The issue was addressed. You can still reply if something is still wrong.' },
                { key: 'closed', label: 'Closed', color: 'bg-red-100 text-red-800 dark:bg-red-500/25 dark:text-red-200 border border-red-300/50 dark:border-red-400/40', meaning: 'The ticket is closed (for example past SLA or fully completed). Contact support if you need it reopened.' },
              ]"""
    c = c[: m.start()] + new_guide + c[m.end() :]
    print("statusGuide ok")
else:
    print("statusGuide miss")

c = c.replace("min-h-[480px] flex flex-col", "flex flex-col")
c = c.replace("min-h-[420px] flex flex-col", "flex flex-col")

if "status-colors-space-v1" not in c:
    c = "/* status-colors-space-v1 */\n" + c
cp.write_text(c)
print("done")
