#!/usr/bin/env python3
from pathlib import Path
p = Path("src/index.css")
t = p.read_text()
old = """html.nexus-light .app-cosmos aside {
  background: #18181b !important;
  border-color: #27272a !important;
  color: #fafafa;
}"""
new = """html.nexus-light .app-cosmos aside {
  background: linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%) !important;
  border-color: rgba(167, 139, 250, 0.4) !important;
  backdrop-filter: blur(18px) saturate(1.1);
  -webkit-backdrop-filter: blur(18px) saturate(1.1);
  color: #0f0a1e;
}"""
if old in t:
    t = t.replace(old, new, 1)
    print("patched light aside from dark")
elif "rgba(255, 255, 255, 0.88)" in t and "html.nexus-light .app-cosmos aside" in t:
    # upgrade white glass to purple gradient
    import re
    t2, n = re.subn(
        r"html\.nexus-light \.app-cosmos aside \{[^}]+\}",
        """html.nexus-light .app-cosmos aside {
  background: linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%) !important;
  border-color: rgba(167, 139, 250, 0.4) !important;
  backdrop-filter: blur(18px) saturate(1.1);
  -webkit-backdrop-filter: blur(18px) saturate(1.1);
  color: #0f0a1e;
}""",
        t,
        count=1,
    )
    if n:
        t = t2
        print("upgraded white to purple gradient")
    else:
        print("aside rule shape miss")
else:
    print("already purple or miss")

old2 = """/* Sidebar stays dark in both themes — keep labels light enough to read */
html.nexus-dark .app-cosmos aside .text-zinc-600,
html.nexus-dark .app-cosmos aside .text-zinc-500,
html.nexus-dark .app-cosmos aside .text-zinc-400,
html.nexus-light .app-cosmos aside .text-zinc-600,
html.nexus-light .app-cosmos aside .text-zinc-500,
html.nexus-light .app-cosmos aside .text-zinc-400 {
  color: #e4e4e7 !important;
}
html.nexus-dark .app-cosmos aside .text-zinc-100,
html.nexus-light .app-cosmos aside .text-zinc-100 {
  color: #fafafa !important;
}"""
new2 = """/* Sidebar: dark theme keeps light labels; light theme uses dark labels */
html.nexus-dark .app-cosmos aside .text-zinc-600,
html.nexus-dark .app-cosmos aside .text-zinc-500,
html.nexus-dark .app-cosmos aside .text-zinc-400 {
  color: #e4e4e7 !important;
}
html.nexus-light .app-cosmos aside .text-zinc-600,
html.nexus-light .app-cosmos aside .text-zinc-500,
html.nexus-light .app-cosmos aside .text-zinc-400 {
  color: #52525b !important;
}
html.nexus-dark .app-cosmos aside .text-zinc-100 {
  color: #fafafa !important;
}
html.nexus-light .app-cosmos aside .text-zinc-100 {
  color: #18181b !important;
}"""
if old2 in t:
    t = t.replace(old2, new2, 1)
    print("patched text colors")
p.write_text(t)
