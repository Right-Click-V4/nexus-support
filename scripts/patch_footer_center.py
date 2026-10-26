#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()

old = """        <footer className="portal-footer relative z-20 shrink-0 px-4 lg:px-6 py-3.5">
          <div className="max-w-5xl mx-auto flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-center sm:text-left">
            <div className="text-[11px] sm:text-xs font-medium tracking-wide portal-footer-brand">
              NexusOps Customer Portal · © 2026 Lizer &amp; Kirzhian
            </div>
            <div className="flex items-center justify-center sm:justify-end gap-3 text-[11px] portal-footer-links">
              <span className="inline-flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Support online
              </span>
              <span className="opacity-40">·</span>
              <span>Secure · Self-serve</span>
            </div>
          </div>
        </footer>"""

new = """        <footer className="portal-footer relative z-20 shrink-0 px-4 lg:px-6 py-3.5">
          <div className="max-w-5xl mx-auto text-center">
            <div className="text-[11px] sm:text-xs font-medium tracking-wide portal-footer-brand">
              NexusOps Customer Portal · © 2026 Lizer &amp; Kirzhian
            </div>
          </div>
        </footer>"""

if old not in t:
    if "portal-footer-links" not in t and "portal-footer-brand" in t:
        print("already centered")
        raise SystemExit(0)
    raise SystemExit("footer block not found")
t = t.replace(old, new, 1)
p.write_text(t)
print("footer centered")
