"""Improve light-mode text contrast outside dark sidebars."""
from pathlib import Path
tm = Path('src/theme-modes.css')
if not tm.exists():
    print('missing'); raise SystemExit(0)
css = tm.read_text()
if 'LIGHT_TEXT_CONTRAST_V1' in css:
    print('already'); raise SystemExit(0)
css = css.rstrip() + """

/* LIGHT_TEXT_CONTRAST_V1 — readable body text in light mode */
html.nexus-light .app-cosmos,
html.nexus-light .portal-shell {
  color: #18181b !important;
}
html.nexus-light .app-cosmos .text-zinc-100,
html.nexus-light .app-cosmos .text-zinc-200,
html.nexus-light .app-cosmos .text-zinc-300,
html.nexus-light .portal-shell .text-zinc-100,
html.nexus-light .portal-shell .text-zinc-200,
html.nexus-light .portal-shell .text-zinc-300 {
  color: #27272a !important;
}
html.nexus-light .app-cosmos .text-zinc-400,
html.nexus-light .app-cosmos .text-zinc-500,
html.nexus-light .portal-shell .text-zinc-400,
html.nexus-light .portal-shell .text-zinc-500 {
  color: #52525b !important;
}
html.nexus-light .app-cosmos .text-zinc-600,
html.nexus-light .portal-shell .text-zinc-600 {
  color: #3f3f46 !important;
}
html.nexus-light .app-cosmos .text-zinc-700,
html.nexus-light .app-cosmos .text-zinc-800,
html.nexus-light .app-cosmos .text-zinc-900,
html.nexus-light .portal-shell .text-zinc-700,
html.nexus-light .portal-shell .text-zinc-800,
html.nexus-light .portal-shell .text-zinc-900 {
  color: #18181b !important;
}
html.nexus-light .app-cosmos > aside .text-zinc-100,
html.nexus-light .app-cosmos > aside .text-zinc-200,
html.nexus-light .app-cosmos > aside .text-zinc-300,
html.nexus-light .app-cosmos > aside .text-zinc-400 {
  color: #a1a1aa !important;
}
html.nexus-light .app-cosmos > aside .text-zinc-500,
html.nexus-light .app-cosmos > aside .text-zinc-600 {
  color: #71717a !important;
}
html.nexus-light .app-cosmos > aside button.text-white,
html.nexus-light .app-cosmos > aside .text-white {
  color: #ffffff !important;
}
"""
tm.write_text(css)
print('light contrast ok')
