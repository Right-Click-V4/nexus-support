"""Ensure MetricBar uses theme-aware .metric-bar class."""
from pathlib import Path

p = Path('src/components/MetricBar.tsx')
if not p.exists():
    print('MetricBar missing')
    raise SystemExit(0)
s = p.read_text()
old = 'className="bg-gradient-to-r from-zinc-950 via-brand-950 to-zinc-900 text-white rounded-2xl px-5 py-4 flex flex-wrap items-center gap-6 lg:gap-8 shadow-lg border border-white/5"'
new = 'className="metric-bar rounded-2xl px-5 py-4 flex flex-wrap items-center gap-6 lg:gap-8 shadow-lg border"'
if old in s:
    p.write_text(s.replace(old, new, 1))
    print('MetricBar class updated')
elif 'metric-bar' in s:
    print('already themed')
else:
    print('pattern miss')
