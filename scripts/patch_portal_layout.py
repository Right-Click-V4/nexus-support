#!/usr/bin/env python3
"""Community height under marquee + footer at bottom of content panel."""
from pathlib import Path
import re

# --- Community ---
pcc = Path("src/components/PortalCommunityChat.tsx")
if pcc.exists():
    t = pcc.read_text()
    t2, n = re.subn(
        r'className="flex h-\[calc\(100vh-8rem\)\] max-h-\[760px\] bg-white rounded-xl border border-zinc-200 shadow-sm overflow-hidden"',
        'className="portal-community-shell flex flex-1 min-h-0 h-full bg-white/95 dark:bg-zinc-950/80 rounded-xl border border-zinc-200/80 dark:border-white/10 shadow-sm overflow-hidden"',
        t,
        count=1,
    )
    if n:
        pcc.write_text(t2)
        print("community height patched")
    elif "portal-community-shell" in t:
        print("community already")
    else:
        print("community pattern miss")

# --- CustomerPortal ---
cp = Path("src/components/CustomerPortal.tsx")
if cp.exists():
    t = cp.read_text()
    if "view === 'community' ? 'overflow-hidden'" in t:
        print("portal layout already")
    else:
        old_main = """        <main className="relative z-10 flex-1 overflow-y-auto p-3 lg:p-5">
          <div className="max-w-5xl mx-auto">"""
        new_main = """        <main
          className={`relative z-10 flex-1 min-h-0 p-3 lg:p-5 flex flex-col ${
            view === 'community' ? 'overflow-hidden' : 'overflow-y-auto'
          }`}
        >
          <div
            className={`w-full mx-auto flex flex-col flex-1 min-h-0 ${
              view === 'community' ? 'max-w-6xl' : 'max-w-5xl min-h-full'
            }`}
          >
            <div className={`flex-1 min-h-0 ${view === 'community' ? 'flex flex-col' : ''}`}>"""
        if old_main not in t:
            raise SystemExit("CustomerPortal main not found")
        t = t.replace(old_main, new_main, 1)
        old_footer = """          </div>

          <footer className="portal-footer relative z-10 mt-8 mb-2 px-2 py-3.5 rounded-xl">"""
        new_footer = """            </div>

            <footer className="portal-footer relative z-10 mt-auto shrink-0 mb-1 px-2 py-3.5 rounded-xl">"""
        if old_footer not in t:
            raise SystemExit("CustomerPortal footer not found")
        t = t.replace(old_footer, new_footer, 1)
        old_end = """          </footer>
        </main>"""
        new_end = """            </footer>
          </div>
        </main>"""
        if old_end not in t:
            raise SystemExit("CustomerPortal end not found")
        t = t.replace(old_end, new_end, 1)
        cp.write_text(t)
        print("CustomerPortal layout patched")

# --- CSS ---
css = Path("src/portal-lounge.css")
if css.exists():
    t = css.read_text()
    if "portal-community-shell" not in t:
        t = t.rstrip() + """

/* Community fills remaining panel under topbar + optional marquee */
.portal-community-shell {
  min-height: 22rem;
  height: 100%;
}
.portal-shell main {
  min-height: 0;
}
"""
        css.write_text(t)
        print("css patched")
    else:
        print("css already")
print("done")
