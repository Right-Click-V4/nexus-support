#!/usr/bin/env python3
from pathlib import Path
p = Path("src/components/CustomerPortal.tsx")
t = p.read_text()

if "portal-footer" in t and t.find("portal-footer") < t.find("</main>"):
    print("footer already inside main")
    raise SystemExit(0)

old = """          </div>
        </main>

        <footer className="portal-footer relative z-20 shrink-0 px-4 lg:px-6 py-3.5">
          <div className="max-w-5xl mx-auto text-center">
            <div className="text-[11px] sm:text-xs font-medium tracking-wide portal-footer-brand">
              NexusOps Customer Portal · © 2026 Lizer &amp; Kirzhian
            </div>
          </div>
        </footer>
"""

new = """          </div>

          <footer className="portal-footer relative z-10 mt-8 mb-2 px-2 py-3.5 rounded-xl">
            <div className="text-center">
              <div className="text-[11px] sm:text-xs font-medium tracking-wide portal-footer-brand">
                NexusOps Customer Portal · © 2026 Lizer &amp; Kirzhian
              </div>
            </div>
          </footer>
        </main>
"""

if old not in t:
    raise SystemExit("footer block not found for move")
t = t.replace(old, new, 1)
p.write_text(t)
print("footer moved into main")
