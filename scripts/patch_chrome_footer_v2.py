#!/usr/bin/env python3
"""Darker/white chrome outlines; sticky footer for short tabs, after content for long."""
from pathlib import Path

cp = Path("src/components/CustomerPortal.tsx")
c = cp.read_text()

old_wrap = """          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl'
            }`}
          >
            <div className={view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1'}>"""

new_wrap = """          <div
            className={`w-full mx-auto flex flex-col ${
              view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1 flex-1'}>"""

if old_wrap in c:
    c = c.replace(old_wrap, new_wrap, 1)
    print("cp wrap ok")
else:
    c = c.replace(
        "view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl'",
        "view === 'community' ? 'max-w-6xl flex-1 min-h-0' : 'max-w-5xl min-h-full'",
        1,
    )
    c = c.replace(
        "view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1'",
        "view === 'community' ? 'flex-1 min-h-0 flex flex-col' : 'pb-1 flex-1'",
        1,
    )
    print("cp wrap partial")

old_ft = """            <footer className={`portal-footer relative z-10 shrink-0 px-2 py-3.5 rounded-xl ${
              view === 'community' ? 'mt-3 mb-1' : 'mt-8 mb-4'
            }`}>"""
new_ft = """            <footer className={`portal-footer relative z-10 shrink-0 px-2 py-3.5 rounded-xl ${
              view === 'community' ? 'mt-3 mb-1' : 'mt-auto mb-2 pt-6'
            }`}>"""
if old_ft in c:
    c = c.replace(old_ft, new_ft, 1)
    print("cp footer ok")
else:
    c = c.replace(
        "view === 'community' ? 'mt-3 mb-1' : 'mt-8 mb-4'",
        "view === 'community' ? 'mt-3 mb-1' : 'mt-auto mb-2 pt-6'",
        1,
    )
    print("cp footer partial")

if "chrome-footer-v2" not in c:
    c = c.replace("/* community-glass-v1 */", "/* community-glass-v1 */ /* chrome-footer-v2 */", 1)
    if "chrome-footer-v2" not in c:
        c = c.replace(
            "export default function CustomerPortal",
            "/* chrome-footer-v2 */\nexport default function CustomerPortal",
            1,
        )

cp.write_text(c)
print("cp written")

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    css = path.read_text()
    if "chrome-footer-v2" in css:
        print(f"{path.name}: already")
        continue

    css = css.replace(
        "  margin-top: 2rem !important;\n  margin-bottom: 1rem !important;",
        "  /* margin handled by utility classes / mt-auto */\n  margin-bottom: 0.5rem;",
    )
    css = css.replace(
        "  margin-top: 1.5rem;\n  position: relative;\n  clear: both;",
        "  position: relative;\n  clear: both;",
    )

    css += """

/* chrome-footer-v2 — outlines + sticky footer for short tabs */
html.nexus-light .portal-sidebar,
html.nexus-light .app-cosmos aside.portal-sidebar,
html.nexus-light aside.portal-sidebar,
.app-cosmos > aside.portal-sidebar {
  border-right: 1px solid rgba(76, 29, 149, 0.55) !important;
  box-shadow: 1px 0 0 rgba(91, 33, 182, 0.18);
}
html.nexus-light .nexus-topbar,
html.nexus-light .portal-shell .nexus-topbar {
  border-bottom: 1px solid rgba(76, 29, 149, 0.5) !important;
  box-shadow: 0 1px 0 rgba(91, 33, 182, 0.15);
}
html.nexus-dark .portal-sidebar,
html.nexus-dark .app-cosmos aside.portal-sidebar {
  border-right: 1px solid rgba(255, 255, 255, 0.22) !important;
  box-shadow: 1px 0 0 rgba(255, 255, 255, 0.06);
}
html.nexus-dark .portal-shell .nexus-topbar,
html.nexus-dark .nexus-topbar {
  border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.05);
}

/* Short tabs: footer at bottom of main panel; long tabs: after content */
.portal-shell main {
  display: flex;
  flex-direction: column;
}
.portal-shell main > div {
  flex: 1 0 auto;
}
"""
    path.write_text(css)
    print(f"{path.name}: chrome-footer-v2 added")

print("done")
