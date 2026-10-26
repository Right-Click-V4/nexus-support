#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()

if "PortalAnnouncementMarquee" not in t:
    if "import PortalHome from './PortalHome';" in t:
        t = t.replace(
            "import PortalHome from './PortalHome';",
            "import PortalHome from './PortalHome';\nimport PortalAnnouncementMarquee from './PortalAnnouncementMarquee';",
            1,
        )
    else:
        raise SystemExit("import anchor missing")

if "<PortalAnnouncementMarquee" not in t:
    old = """        </header>

        <main className=\"relative z-10 flex-1 overflow-y-auto p-3 lg:p-5\">
"""
    new = """        </header>

        <PortalAnnouncementMarquee />

        <main className=\"relative z-10 flex-1 overflow-y-auto p-3 lg:p-5\">
"""
    if old not in t:
        raise SystemExit("header/main anchor missing")
    t = t.replace(old, new, 1)

p.write_text(t)
print("marquee wired")
