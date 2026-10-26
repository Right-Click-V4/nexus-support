#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()
t2 = t
t2 = t2.replace(
  "home: { title: 'Home', desc: 'Self-serve help and quick actions for your account.', iconColor: 'text-violet-500' },",
  "home: { title: 'Overview', desc: 'How this portal works and how to get support.', iconColor: 'text-violet-500' },",
  1,
)
t2 = t2.replace(
  "{ id: 'home', label: 'Home', icon: Home },",
  "{ id: 'home', label: 'Overview', icon: Home },",
  1,
)
t2 = t2.replace(
  'className="px-4 py-2 border border-zinc-200 text-sm rounded-lg bg-white/80 hover:bg-white">Home</button>',
  'className="px-4 py-2 border border-zinc-200 text-sm rounded-lg bg-white/80 hover:bg-white">Overview</button>',
  1,
)
if t2 == t:
  print("no changes or already renamed")
else:
  p.write_text(t2)
  print("renamed Home -> Overview")
