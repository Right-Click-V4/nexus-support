#!/usr/bin/env python3
"""Light-mode glass + Community logo contrast for portal Community chat."""
from pathlib import Path

p = Path('src/components/PortalCommunityChat.tsx')
if not p.exists():
    print('skip community: missing')
    raise SystemExit(0)
t = p.read_text()
changed = False

old_shell = 'portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/5 dark:bg-[#0c0a14]/30 border-white/30 dark:border-violet-500/25 backdrop-blur-sm shadow-sm'
new_shell = 'portal-community-shell portal-overview-glass flex flex-1 min-h-0 h-full rounded-xl overflow-hidden'
if old_shell in t:
    t = t.replace(old_shell, new_shell)
    changed = True
    print('shell glass')

for old, new in [
    (
        'border-r border-white/25 dark:border-white/10 bg-transparent flex flex-col hidden sm:flex backdrop-blur-md',
        'border-r border-zinc-200/40 dark:border-white/10 bg-white/40 dark:bg-black/20 flex flex-col hidden sm:flex backdrop-blur-md',
    ),
    (
        'border-l border-white/25 dark:border-white/10 bg-transparent text-zinc-800 dark:text-zinc-100',
        'border-l border-zinc-200/40 dark:border-white/10 bg-white/40 dark:bg-black/20 text-zinc-800 dark:text-zinc-100',
    ),
]:
    if old in t:
        t = t.replace(old, new)
        changed = True
        print('rail', old[:40])

old_logo = '<Users size={24} className="text-violet-400" />'
new_logo = '<Users size={24} className="text-violet-700 dark:text-violet-300" />'
if old_logo in t:
    t = t.replace(old_logo, new_logo)
    changed = True
    print('logo users')

old_hash = '<Hash size={24} className="text-zinc-400" />'
new_hash = '<Hash size={24} className="text-zinc-600 dark:text-zinc-400" />'
if old_hash in t:
    t = t.replace(old_hash, new_hash)
    changed = True
    print('logo hash')

old_ring = 'w-14 h-14 rounded-full bg-violet-500/15 dark:bg-zinc-800/90 flex items-center justify-center mb-2 ring-1 ring-violet-500/30'
new_ring = 'w-14 h-14 rounded-full bg-violet-600/20 dark:bg-zinc-800/90 flex items-center justify-center mb-2 ring-2 ring-violet-600/40 dark:ring-violet-500/30 shadow-sm'
if old_ring in t:
    t = t.replace(old_ring, new_ring)
    changed = True
    print('logo ring')

if changed:
    p.write_text(t)
    print('community glass patched', len(t))
else:
    print('community already patched or patterns missing')
