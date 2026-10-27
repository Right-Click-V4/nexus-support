#!/usr/bin/env python3
"""Slightly darken Customer Portal top bar + sidebar (light + dark)."""
from pathlib import Path

MARKER = "/* chrome-darker-v1 */"

LIGHT_SIDEBAR = (
    "linear-gradient(180deg, rgba(196, 181, 253, 0.92) 0%, "
    "rgba(167, 139, 250, 0.88) 45%, rgba(196, 181, 253, 0.90) 100%)"
)
LIGHT_TOPBAR = (
    "linear-gradient(105deg, rgba(196, 181, 253, 0.94) 0%, "
    "rgba(167, 139, 250, 0.90) 40%, rgba(221, 214, 254, 0.92) 100%)"
)
DARK_SIDEBAR = "rgba(8, 5, 20, 0.88)"
DARK_TOPBAR = "rgba(8, 6, 22, 0.72)"

OLD_LIGHT_SIDEBAR = (
    "linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, "
    "rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%)"
)
OLD_LIGHT_TOPBAR = (
    "linear-gradient(105deg, rgba(237, 233, 254, 0.95) 0%, "
    "rgba(221, 214, 254, 0.9) 40%, rgba(245, 243, 255, 0.92) 100%)"
)
OLD_LIGHT_TOPBAR2 = (
    "linear-gradient(105deg, rgba(237, 233, 254, 0.92) 0%, "
    "rgba(221, 214, 254, 0.88) 45%, rgba(233, 213, 255, 0.9) 100%)"
)

for path in [Path("src/portal-lounge.css"), Path("src/index.css")]:
    if not path.exists():
        continue
    css = path.read_text()
    if MARKER in css:
        print(f"{path.name}: already")
        continue

    n = 0
    for old in (
        OLD_LIGHT_SIDEBAR,
        "linear-gradient(180deg, rgba(237, 233, 254, 0.95) 0%, rgba(221, 214, 254, 0.92) 50%, rgba(245, 243, 255, 0.94) 100%)",
    ):
        if old in css:
            css = css.replace(old, LIGHT_SIDEBAR)
            n += 1

    for old in (OLD_LIGHT_TOPBAR, OLD_LIGHT_TOPBAR2):
        if old in css:
            css = css.replace(old, LIGHT_TOPBAR)
            n += 1

    css2 = css.replace(
        "background: rgba(12, 8, 28, 0.78) !important;",
        f"background: {DARK_SIDEBAR} !important;",
    )
    if css2 != css:
        css = css2
        n += 1
    css2 = css.replace(
        "background: rgba(12, 10, 28, 0.55);",
        f"background: {DARK_TOPBAR};",
    )
    if css2 != css:
        css = css2
        n += 1

    css += f"""

{MARKER}
html.nexus-light .portal-sidebar,
html.nexus-light .app-cosmos aside.portal-sidebar,
html.nexus-light aside.portal-sidebar,
.app-cosmos > aside.portal-sidebar {{
  background: {LIGHT_SIDEBAR} !important;
}}
html.nexus-light .nexus-topbar,
html.nexus-light .portal-shell .nexus-topbar {{
  background: {LIGHT_TOPBAR} !important;
}}
html.nexus-dark .portal-sidebar,
html.nexus-dark .app-cosmos aside.portal-sidebar {{
  background: {DARK_SIDEBAR} !important;
}}
html.nexus-dark .portal-shell .nexus-topbar {{
  background: {DARK_TOPBAR} !important;
}}
"""
    path.write_text(css)
    print(f"{path.name}: darkened ({n} inline replaces + override block)")

print("done")
