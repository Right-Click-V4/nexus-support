#!/usr/bin/env python3
"""Fix incoming bubble contrast; true glass community rails (stop sidebar CSS leaking)."""
from pathlib import Path
import re

pcc = Path("src/components/PortalCommunityChat.tsx")
t = pcc.read_text()

old_bubble = """                  className={`max-w-[78%] rounded-2xl px-3.5 py-2.5 text-sm relative shadow-sm ${
                    mine
                      ? 'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white rounded-br-md'
                      : 'bg-white/70 dark:bg-[#1c1830]/95 border border-white/30 dark:border-violet-500/15 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'
                  }`}"""

new_bubble = """                  className={`max-w-[78%] rounded-2xl px-3.5 py-2.5 text-sm relative shadow-sm ${
                    mine
                      ? 'bg-gradient-to-br from-violet-600 to-fuchsia-600 text-white rounded-br-md'
                      : 'community-msg-other bg-violet-100/95 dark:bg-[#2a2448]/92 border border-violet-200/60 dark:border-violet-500/20 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'
                  }`}"""

if old_bubble in t:
    t = t.replace(old_bubble, new_bubble, 1)
    print("bubble ok")
else:
    t2, n = re.subn(
        r": 'bg-white/70 dark:bg-\[#1c1830\]/95 border border-white/30 dark:border-violet-500/15 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'",
        ": 'community-msg-other bg-violet-100/95 dark:bg-[#2a2448]/92 border border-violet-200/60 dark:border-violet-500/20 text-zinc-900 dark:text-zinc-100 rounded-bl-md backdrop-blur-sm'",
        t,
        count=1,
    )
    if n:
        t = t2
        print("bubble loose ok")
    else:
        print("bubble miss")

t = t.replace(
    "${mine ? 'text-white/60' : 'text-zinc-400'}",
    "${mine ? 'text-white/70' : 'text-zinc-600 dark:text-zinc-400'}",
    1,
)

t = t.replace(
    'className="w-56 shrink-0 border-r border-white/20 dark:border-white/10 bg-white/10 dark:bg-[#0a0812]/50 flex flex-col hidden sm:flex backdrop-blur-md"',
    'className="portal-community-rail portal-community-rail--left w-56 shrink-0 border-r border-white/25 dark:border-white/10 bg-transparent flex flex-col hidden sm:flex backdrop-blur-md"',
    1,
)
t = t.replace(
    'className="w-72 shrink-0 border-l border-white/20 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/70 text-zinc-800 dark:text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md"',
    'className="portal-community-rail portal-community-rail--right w-72 shrink-0 border-l border-white/25 dark:border-white/10 bg-transparent text-zinc-800 dark:text-zinc-100 flex flex-col overflow-y-auto backdrop-blur-md"',
    1,
)

t = t.replace(
    'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/10 dark:bg-[#0c0a14]/45 border-white/25 dark:border-violet-500/25 backdrop-blur-md shadow-sm"',
    'className="portal-community-shell flex flex-1 min-h-0 h-full rounded-xl border overflow-hidden bg-white/5 dark:bg-[#0c0a14]/30 border-white/30 dark:border-violet-500/25 backdrop-blur-sm shadow-sm"',
    1,
)
t = t.replace(
    'className="flex-1 flex flex-col min-w-0 bg-violet-950/10 dark:bg-[#0c0a16]/35"',
    'className="flex-1 flex flex-col min-w-0 bg-transparent"',
    1,
)
t = t.replace(
    'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/15 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/55 backdrop-blur"',
    'className="flex items-center gap-2 px-3 sm:px-4 py-3 border-b border-white/20 dark:border-white/10 bg-white/10 dark:bg-black/20 backdrop-blur-sm"',
    1,
)
t = t.replace(
    "border-t border-white/15 dark:border-white/10 bg-white/15 dark:bg-[#0c0a16]/55 backdrop-blur",
    "border-t border-white/20 dark:border-white/10 bg-white/10 dark:bg-black/20 backdrop-blur-sm",
    1,
)

if "community-contrast-v1" not in t:
    t = t.replace("/* community-glass-v1 */", "/* community-glass-v1 */ /* community-contrast-v1 */", 1)
    if "community-contrast-v1" not in t:
        t = t.replace(
            "export default function PortalCommunityChat",
            "/* community-contrast-v1 */\nexport default function PortalCommunityChat",
            1,
        )

pcc.write_text(t)
print("pcc done")

for css_path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not css_path.exists():
        continue
    css = css_path.read_text()
    changed = False

    broad = """html.nexus-light .app-cosmos aside,
html.nexus-light .app-cosmos aside.portal-sidebar,
html.nexus-light aside.portal-sidebar {
  background: linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%) !important;
  border-color: rgba(167, 139, 250, 0.4) !important;
  border-right: 1px solid rgba(167, 139, 250, 0.4) !important;
  color: #0f0a1e !important;
  backdrop-filter: blur(18px) saturate(1.1) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.1) !important;
}"""
    narrow = """html.nexus-light .app-cosmos aside.portal-sidebar,
html.nexus-light aside.portal-sidebar {
  background: linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%) !important;
  border-color: rgba(167, 139, 250, 0.4) !important;
  border-right: 1px solid rgba(167, 139, 250, 0.4) !important;
  color: #0f0a1e !important;
  backdrop-filter: blur(18px) saturate(1.1) !important;
  -webkit-backdrop-filter: blur(18px) saturate(1.1) !important;
}"""
    if broad in css:
        css = css.replace(broad, narrow, 1)
        changed = True
        print(f"{css_path.name}: narrowed aside rule")
    elif "html.nexus-light .app-cosmos aside," in css:
        css = css.replace(
            "html.nexus-light .app-cosmos aside,\nhtml.nexus-light .app-cosmos aside.portal-sidebar,",
            "html.nexus-light .app-cosmos aside.portal-sidebar,",
            1,
        )
        changed = True
        print(f"{css_path.name}: narrowed aside rule (partial)")

    css = css.replace(
        "html.nexus-light .app-cosmos aside .portal-sidebar-title,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .portal-sidebar-title,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .portal-nav-item,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .portal-nav-item,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .portal-sidebar-sub,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .portal-sidebar-sub,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .portal-sidebar-label",
        "html.nexus-light .app-cosmos aside.portal-sidebar .portal-sidebar-label",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-100,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-100,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-200,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-200,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-300",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-300",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-400,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-400,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-500,",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-500,",
    )
    css = css.replace(
        "html.nexus-light .app-cosmos aside .text-zinc-600",
        "html.nexus-light .app-cosmos aside.portal-sidebar .text-zinc-600",
    )

    if "community-contrast-v1" not in css:
        css += """

/* community-contrast-v1 — real glass rails + readable other-user bubbles */
html.nexus-light .portal-community-shell,
html.nexus-dark .portal-community-shell {
  background: rgba(255, 255, 255, 0.06) !important;
}
html.nexus-dark .portal-community-shell {
  background: rgba(12, 10, 20, 0.28) !important;
}
.portal-community-rail {
  background: transparent !important;
  background-image: none !important;
}
html.nexus-light .portal-community-rail {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #1e1b4b !important;
}
html.nexus-dark .portal-community-rail {
  background: rgba(8, 6, 18, 0.22) !important;
  color: #f4f4f5 !important;
}
.portal-community-shell .community-msg-other {
  background: rgba(237, 233, 254, 0.95) !important;
  color: #1e1b4b !important;
  border-color: rgba(167, 139, 250, 0.35) !important;
}
html.nexus-dark .portal-community-shell .community-msg-other {
  background: rgba(42, 36, 72, 0.92) !important;
  color: #f4f4f5 !important;
  border-color: rgba(139, 92, 246, 0.25) !important;
}
.portal-community-shell .community-msg-other .text-violet-600 {
  color: #6d28d9 !important;
}
html.nexus-dark .portal-community-shell .community-msg-other .text-violet-300,
html.nexus-dark .portal-community-shell .community-msg-other .dark\\:text-violet-300 {
  color: #c4b5fd !important;
}
"""
        changed = True
        print(f"{css_path.name}: contrast CSS added")

    if changed:
        css_path.write_text(css)

print("done")
